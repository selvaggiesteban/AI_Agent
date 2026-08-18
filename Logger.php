<?php
class Logger {
    private static $logFile = __DIR__ . '/logs/activity.log';

    public static function log($message, $level = 'INFO') {
        if (!is_dir(__DIR__ . '/logs')) {
            mkdir(__DIR__ . '/logs', 0755, true);
        }
        $date = date('Y-m-d H:i:s');
        $entry = "[$date] [$level] $message" . PHP_EOL;
        file_put_contents(self::$logFile, $entry, FILE_APPEND);
    }

    public static function info($msg) { self::log($msg, 'INFO'); }
    public static function warn($msg) { self::log($msg, 'WARN'); }
    public static function error($msg) { self::log($msg, 'ERROR'); }
}
