<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;
class CourseProgress extends Model {
    protected $table = 'course_progresses';
    protected $fillable = ['learner_id', 'progress'];
}
