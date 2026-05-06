<?php
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
Schema::create('course_progresses', function (Blueprint $table) {
    $table->id();
    $table->foreignId('learner_id');
    $table->integer('progress');
    $table->timestamps();
});
