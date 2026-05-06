<?php
namespace App\Http\Controllers;
use App\Services\CourseProgressService;
class ScormCommitController {
    public function __construct(private CourseProgressService $progressService) {}
    public function commit(Request $request) {
        $this->progressService->commit($request->all());
    }
}
