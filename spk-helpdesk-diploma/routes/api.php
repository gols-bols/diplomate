<?php

use App\Http\Controllers\Api\AuthApiController;
use App\Http\Controllers\Api\TicketApiController;
use Illuminate\Support\Facades\Route;

Route::prefix('v1')->group(function (): void {
    Route::post('/login', [AuthApiController::class, 'login']);

    Route::middleware('api.token')->group(function (): void {
        Route::post('/logout', [AuthApiController::class, 'logout']);
        Route::get('/tickets', [TicketApiController::class, 'index']);
        Route::post('/tickets', [TicketApiController::class, 'store']);
        Route::get('/tickets/{ticket}', [TicketApiController::class, 'show']);
        Route::put('/tickets/{ticket}', [TicketApiController::class, 'update']);
    });
});
