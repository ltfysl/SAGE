<?php
namespace App\Services;
use App\Models\CourseProgress;
use App\Models\LearningContentProgress;

class CourseProgressService
{
    public function commit(array $data)
    {
        return CourseProgress::updateOrCreate(
            ['learner_id' => $data['learner_id']],
            ['progress' => $data['progress']]
        );
    }

    public function updateProgress(int $learnerId, int $progress)
    {
        CourseProgress::where('learner_id', $learnerId)->update(['progress' => $progress]);
        LearningContentProgress::where('learner_id', $learnerId)->update(['status' => 'completed']);
    }
}
