var gulp = require('gulp'),
    sass = require('gulp-sass'),
    concat = require('gulp-concat'),
    minifyCSS = require('gulp-minify-css'),
    autoprefixer = require('gulp-autoprefixer'),
    uglify = require('gulp-uglify'),
    del = require('del');

// sprites?
// add js minification for blog + admin
var paths = {
  applicationScss: ['photolog/static/scss/application.scss'],
  styles: ['photolog/static/scss/app/*.scss'],
  scriptsLibs: ['photolog/static/vendor/*.js'],
  scriptsApp: ['photolog/static/js/*.js'],
}

gulp.task('clean-scss', function(cb) {
  del(['.public/app.min.css'], function(err, deletedFiles) {
    console.log('Files cleaned: ', deletedFiles.join(', '));
    cb();
  });
});

gulp.task('clean-blog-js', function(cb) {
  del(['./public/blog.min.js'], function(err, deletedFiles) {
    console.log('Files cleaned: ', deletedFiles.join(', '));
    cb();
  });
});

gulp.task('scss', ['clean-scss'], function() {
  return gulp.src(paths.applicationScss)
    .pipe(autoprefixer({
      cascade: false,
    }))
    .pipe(sass({includePaths: [paths.styles]}))
    .pipe(minifyCSS())
    .pipe(concat('app.min.css'))
    .pipe(gulp.dest('./public/'));
});

gulp.task('js', ['clean-blog-js'], function() {
  return gulp.src(paths.scriptsLibs.concat(paths.scriptsApp))
    .pipe(uglify())
    .pipe(concat('blog.min.js'))
    .pipe(gulp.dest('./public/'));
});

gulp.task('copy-assets', [], function() {
  return gulp.src('photolog/static/assets/*')
    .pipe(gulp.dest('./public/'));
});

gulp.task('watch', function() {
  gulp.watch(paths.styles.concat(paths.applicationScss), ['scss']);
  gulp.watch(paths.scriptsLibs.concat(paths.scriptsApp), ['js']);
  gulp.watch('photolog/static/assets/*', ['copy-assets']);
});

gulp.task('default', ['watch', 'scss', 'js', 'copy-assets']);
