<?php

namespace App\Console\Commands;

use Illuminate\Foundation\Console\ServeCommand as BaseServeCommand;

use function Illuminate\Support\php_binary;

/**
 * Built-in PHP server (php -S) does not inherit -d flags from the parent "php artisan serve" process.
 * Pass upload_tmp_dir and size limits to the child server with an absolute path (cwd is public/).
 */
class ServeCommand extends BaseServeCommand
{
    protected function serverCommand(): array
    {
        $uploadTmp = $this->ensureUploadTmpDir();

        $server = file_exists(base_path('server.php'))
            ? base_path('server.php')
            : dirname((new \ReflectionClass(BaseServeCommand::class))->getFileName()).'/../resources/server.php';

        return [
            php_binary(),
            '-d', 'upload_max_filesize=8M',
            '-d', 'post_max_size=12M',
            '-d', 'upload_tmp_dir='.$uploadTmp,
            '-S',
            $this->host().':'.$this->port(),
            $server,
        ];
    }

    private function ensureUploadTmpDir(): string
    {
        require_once base_path('bootstrap/upload_dirs.php');

        $dir = storage_path('framework/uploads');
        $resolved = realpath($dir);

        return $resolved !== false ? $resolved : $dir;
    }
}
