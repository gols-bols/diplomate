<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('users', function (Blueprint $table): void {
            $table->enum('campus', ['main', '1', '2', '3'])->nullable()->after('role');
        });

        Schema::table('tickets', function (Blueprint $table): void {
            $table->string('requester_name')->nullable()->after('status');
            $table->enum('campus', ['main', '1', '2', '3'])->default('main')->after('requester_name');
            $table->string('room', 50)->nullable()->after('campus');
            $table->foreignId('assignee_id')->nullable()->after('created_by')->constrained('users')->nullOnDelete();
        });
    }

    public function down(): void
    {
        Schema::table('tickets', function (Blueprint $table): void {
            $table->dropConstrainedForeignId('assignee_id');
            $table->dropColumn(['requester_name', 'campus', 'room']);
        });

        Schema::table('users', function (Blueprint $table): void {
            $table->dropColumn('campus');
        });
    }
};
