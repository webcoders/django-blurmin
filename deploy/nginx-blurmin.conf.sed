# REPLACE '#pwd#' WITH YOUR PROJECT PATH!!!!

server {
	listen 80;

	index index.html index.htm index.nginx-debian.html;

	server_name blurmin;

	location / {
	    proxy_pass http://127.0.0.1:8000;
	}

#	location /notifications/ {
#	    proxy_pass http://127.0.0.1:8000;
#	    proxy_http_version 1.1;
#	    proxy_set_header Upgrade $http_upgrade;
#	    proxy_set_header Connection "upgrade";
#	}


#	location /dashboard {
#		# First attempt to serve request as file, then
#		# as directory, then fall back to displaying a 404.
#		#try_files $uri $uri/ =404;
#	        proxy_pass http://127.0.0.1:8000;
#	}

    location /static {
    	root  #pwd#/;
    }

    location /bower_components {
            root   #pwd#/static/ui/;
    }


    location /dashboard/app/ {
            alias   #pwd#/static/ui/blur-admin/app/;
    }

    location /dashboard/assets/ {
            alias   #pwd#/static/ui/blur-admin/assets/;
    }

    location /dashboard/fonts/ {
            alias   #pwd#/static/ui/blur-admin/fonts/;
    }

    location /dashboard/lib {
            alias   #pwd#/static/ui/blur-admin/lib/;
    }

    location /dashboard/sass/ {
            alias   #pwd#/static/ui/blur-admin/sass/;
    }

}
