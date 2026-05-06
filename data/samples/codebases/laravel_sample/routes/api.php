<?php
use App\Http\Controllers\ScormCommitController;
Route::post('/scorm/commit', [ScormCommitController::class, 'commit']);
Route::get('/scorm/status/{id}', [ScormCommitController::class, 'status']);
