<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('tickets', function (Blueprint $table): void {
            $table->enum('category', ['equipment', 'network', 'software', 'access', 'printing', 'other'])
                ->default('other')
                ->after('priority');
            $table->date('deadline')->nullable()->after('room');
        });
    }

    public function down(): void
    {
        Schema::table('tickets', function (Blueprint $table): void {
            $table->dropColumn(['category', 'deadline']);
        });
    }
};
