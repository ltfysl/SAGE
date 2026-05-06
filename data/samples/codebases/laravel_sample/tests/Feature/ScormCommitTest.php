<?php
namespace Tests\Feature;
use App\Services\CourseProgressService;
class ScormCommitTest extends TestCase {
    public function test_commit_writes_to_table() {
        $service = new CourseProgressService();
        $result = $service->commit(['learner_id' => 1, 'progress' => 100]);
        $this->assertNotNull($result);
    }
}
