var gulp = require('gulp');
var browserify = require('browserify');
var source = require('vinyl-source-stream');

gulp.task('build', ['content']);

gulp.task('content', function() {
    return browserify('./static/javascripts/application.js')
        .bundle()
        .pipe(source('nf.js'))
        .pipe(gulp.dest('./static/javascripts/'));
});