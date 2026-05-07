<?php
namespace App\Http\Controllers;
use App\Services\CourseProgressService;
use App\Jobs\SendCertificateMail;

class ScormCommitController
{
    public function __construct(private CourseProgressService $progressService) {}

    public function commit(Request $request)
    {
        $data = $request->all();
        $this->progressService->commit($data);
        $this->progressService->updateProgress($data['learner_id'], $data['progress']);
        SendCertificateMail::dispatch($data['learner_id']);
        return response()->json(['status' => 'ok']);
    }
}
