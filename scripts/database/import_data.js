const fs = require('fs');
const path = require('path');
const mysql = require('mysql2/promise');
const csv = require('csv-parser');

// Configuración de la base de datos
const dbConfig = {
    host: 'localhost',
    user: 'root',
    password: '', // Si tu MySQL tiene contraseña, colócala aquí
    database: 'territorial_db'
};

async function main() {
    console.log('Iniciando proceso de importación...');
    
    let connection;
    try {
        connection = await mysql.createConnection(dbConfig);
        console.log('Conectado a la base de datos territorial_db.');
    } catch (error) {
        console.error('Error al conectar a MySQL:', error.message);
        console.log('Asegúrate de haber creado la base de datos y tener credenciales válidas en import_data.js.');
        return;
    }

    const seedsDir = path.join(__dirname, 'seeds');
    const bbddDir = path.join(__dirname, 'bbdd');

    // 1. IMPORTAR KEYWORDS
    console.log('\n--- Importando Keywords ---');
    const keywordsFile = path.join(seedsDir, 'keywords.txt');
    if (fs.existsSync(keywordsFile)) {
        const keywords = fs.readFileSync(keywordsFile, 'utf8')
            .split('\n')
            .map(l => l.trim())
            .filter(l => l);
            
        let insertedKeywords = 0;
        for (const kw of keywords) {
            try {
                await connection.execute('INSERT IGNORE INTO scrap_keywords (term) VALUES (?)', [kw]);
                insertedKeywords++;
            } catch (err) {
                console.error(`Error insertando keyword "${kw}":`, err.message);
            }
        }
        console.log(`Keywords importadas: ${insertedKeywords}/${keywords.length}`);
    } else {
        console.log('Archivo keywords.txt no encontrado.');
    }

    // 2. IMPORTAR UBICACIONES
    console.log('\n--- Importando Ubicaciones ---');
    const locationsFile = path.join(seedsDir, 'ubicaciones.txt');
    if (fs.existsSync(locationsFile)) {
        const locations = fs.readFileSync(locationsFile, 'utf8')
            .split('\n')
            .map(l => l.trim())
            .filter(l => l);
            
        let insertedLocations = 0;
        for (const loc of locations) {
            try {
                await connection.execute('INSERT IGNORE INTO scrap_locations (name) VALUES (?)', [loc]);
                insertedLocations++;
            } catch (err) {
                console.error(`Error insertando ubicación "${loc}":`, err.message);
            }
        }
        console.log(`Ubicaciones importadas: ${insertedLocations}/${locations.length}`);
    } else {
        console.log('Archivo ubicaciones.txt no encontrado.');
    }

    // 3. IMPORTAR RESULTADOS CSV (BBDD)
    console.log('\n--- Importando Leads desde CSV en bbdd/ ---');
    if (fs.existsSync(bbddDir)) {
        const files = fs.readdirSync(bbddDir).filter(f => f.endsWith('.csv'));
        console.log(`Encontrados ${files.length} archivos CSV.`);

        for (const file of files) {
            console.log(`Procesando archivo: ${file}`);
            const filePath = path.join(bbddDir, file);
            
            // Intentar extraer la keyword del nombre del archivo si es posible
            let fileKeywordId = null;
            let fileKeywordStr = '';
            
            // Los archivos a veces tienen el formato UUID KEYWORD.csv
            const fileNameParts = file.replace('.csv', '').split(' ');
            if (fileNameParts.length > 1) {
                fileKeywordStr = fileNameParts.slice(1).join(' ');
                
                // Si encontramos una keyword en el nombre, obtener su ID
                const [kwRows] = await connection.execute('SELECT id FROM scrap_keywords WHERE term = ?', [fileKeywordStr]);
                if (kwRows.length > 0) {
                    fileKeywordId = kwRows[0].id;
                } else {
                    // Si no existe, crearla
                    await connection.execute('INSERT IGNORE INTO scrap_keywords (term) VALUES (?)', [fileKeywordStr]);
                    const [newKwRows] = await connection.execute('SELECT id FROM scrap_keywords WHERE term = ?', [fileKeywordStr]);
                    if (newKwRows.length > 0) {
                        fileKeywordId = newKwRows[0].id;
                    }
                }
            }

            await new Promise((resolve, reject) => {
                let count = 0;
                fs.createReadStream(filePath)
                    .pipe(csv())
                    .on('data', async (row) => {
                        // Place ID es obligatorio en el esquema como clave única
                        if (!row.place_id && !row.cid) return; 
                        
                        const placeId = row.place_id || row.cid || `generated_${Date.now()}_${Math.random()}`;

                        const title = row.title || 'Sin Titulo';
                        const category = row.category || null;
                        const address = row.address || null;
                        const phone = row.phone || null;
                        const website = row.website || null;
                        const emails = row.emails || null;
                        const google_link = row.link || null;
                        const cid = row.cid || null;
                        const input_id = row.input_id || null;
                        const open_hours = row.open_hours || null;
                        const complete_address = row.complete_address || null;
                        
                        const review_count = parseInt(row.review_count) || 0;
                        const review_rating = parseFloat(row.review_rating) || null;
                        const latitude = parseFloat(row.latitude) || null;
                        const longitude = parseFloat(row.longitude) || null;

                        try {
                            const query = `
                                INSERT IGNORE INTO scrap_leads 
                                (input_id, place_id, title, category, address, phone, website, emails, review_count, review_rating, latitude, longitude, cid, google_link, open_hours, complete_address, keyword_id)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            `;
                            
                            const values = [
                                input_id, place_id, title, category, address, phone, website, emails, review_count, review_rating, latitude, longitude, cid, google_link, open_hours, complete_address, fileKeywordId
                            ];
                            
                            await connection.execute(query, values);
                            count++;
                        } catch (err) {
                            // Errores ignorados si son duplicados
                            if (err.code !== 'ER_DUP_ENTRY') {
                                console.error('Error insertando row:', err.message);
                            }
                        }
                    })
                    .on('end', () => {
                        console.log(`  -> Insertados/procesados ${count} leads del archivo ${file}`);
                        resolve();
                    })
                    .on('error', (err) => {
                        console.error(`  -> Error procesando archivo ${file}:`, err);
                        resolve(); // Resolve anyway to continue with next file
                    });
            });
        }
    } else {
        console.log('Directorio bbdd/ no encontrado.');
    }

    console.log('\nImportación finalizada.');
    await connection.end();
}

main();