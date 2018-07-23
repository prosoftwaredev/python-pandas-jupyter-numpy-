'use strict';

var gulp = require('gulp');
var sass = require('gulp-sass');
var sourcemaps = require('gulp-sourcemaps');
var browserSync = require('browser-sync').create();

gulp.task('sass', function () {
    return gulp.src('src/benchmark/static/scss/*.scss')
        .pipe(sourcemaps.init())
        .pipe(sass().on('error', sass.logError))
        .pipe(sourcemaps.write(''))
        .pipe(gulp.dest('src/benchmark/static/css'))
        .pipe(browserSync.stream());
});

gulp.task('sass:watch', function () {
    gulp.watch('src/benchmark/static/scss/**/*.scss', ['sass']);
});

// Static Server + watching scss/html files
gulp.task('serve', ['sass'], function() {

    browserSync.init({
        proxy: "127.0.0.1:5100"
    });

    gulp.watch("src/benchmark/static/scss/**/*.scss", ['sass']);
    gulp.watch("src/**/*.html").on('change', browserSync.reload);
});

gulp.task('default', [ 'sass' ]);
