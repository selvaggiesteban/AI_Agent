<?php
require_once 'Logger.php';

// Configuration
$CONFIG = [
    'db_host' => 'localhost',
    'db_name' => 'oteguiobra_web',
    'db_user' => 'oteguiobra_web',
    'db_pass' => '', // Leave empty if using .env or set here
    'backup_dir' => __DIR__ . '/backups',
    'folders_to_backup' => ['images', 'api', 'cvs'],
];

// Try to load DB pass from .env if available
if (file_exists(__DIR__ . '/api/.env')) {
    $env = parse_ini_file(__DIR__ . '/api/.env');
    if (isset($env['DB_PASS'])) $CONFIG['db_pass'] = $env['DB_PASS'];
}

function createBackup() {
    global $CONFIG;
    Logger::info('Starting backup process...');

    if (!is_dir($CONFIG['backup_dir'])) {
        mkdir($CONFIG['backup_dir'], 0755, true);
    }

    $timestamp = date('Ymd_His');
    $backupName = "backup_$timestamp";
    $backupPath = $CONFIG['backup_dir'] . "/$backupName";
    mkdir($backupPath, 0755, true);

    // 1. Database Backup
    $dbFile = "$backupPath/database.sql";
    $cmd = sprintf(
        'mysqldump -h %s -u %s -p%s %s > %s',
        escapeshellarg($CONFIG['db_host']),
        escapeshellarg($CONFIG['db_user']),
        escapeshellarg($CONFIG['db_pass']),
        escapeshellarg($CONFIG['db_name']),
        escapeshellarg($dbFile)
    );

    exec($cmd, $output, $result);
    if ($result === 0) {
        Logger::info("Database backup created: database.sql");
    } else {
        Logger::error("Database backup failed. mysqldump might not be available or credentials wrong.");
    }

    // 2. Files Backup
    $filesZip = "$backupPath/files.zip";
    $zip = new ZipArchive();
    if ($zip->open($filesZip, ZipArchive::CREATE) === TRUE) {
        foreach ($CONFIG['folders_to_backup'] as $folder) {
            $dirPath = __DIR__ . '/' . $folder;
            if (is_dir($dirPath)) {
                $files = new RecursiveIteratorIterator(
                    new RecursiveDirectoryIterator($dirPath, RecursiveDirectoryIterator::SKIP_DOTS),
                    RecursiveIteratorIterator::SELF_FIRST
                );
                foreach ($files as $file) {
                    if (!$file->isDir()) {
                        $filePath = $file->getRealPath();
                        $relativePath = substr($filePath, strlen(__DIR__) + 1);
                        $zip->addFile($filePath, $relativePath);
                    }
                }
            }
        }
        $zip->close();
        Logger::info("Files backup created: files.zip");
    } else {
        Logger::error("Files backup failed. ZipArchive error.");
    }

    return $backupName;
}

// Simple CLI/Web execution
if (php_sapi_name() === 'cli' || isset($_GET['run'])) {
    try {
        $name = createBackup();
        echo "Backup completed successfully: $name";
    } catch (Exception $e) {
        echo "Backup failed: " . $e->getMessage();
    }
} else {
    echo "Use ?run=1 to trigger backup.";
}
