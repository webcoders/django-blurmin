mkdir static && ln -s `pwd`/ui/static/ui   static/ui
cp deploy/nginx-blurmin.conf.sed deploy/nginx-blurmin.conf
sed -i "s|#pwd#|$(pwd)|g" deploy/nginx-blurmin.conf
