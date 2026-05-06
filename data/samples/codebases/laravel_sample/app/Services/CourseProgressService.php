<?php
namespace App\Services;
use App\Models\CourseProgress;
class CourseProgressService {
    public function commit(array $data) {
        return CourseProgress::updateOrCreate(
            ['learner_id' => $data['learner_id']],
            ['progress' => $data['progress']]
        );
    }
}
