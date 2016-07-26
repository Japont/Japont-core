echo "-----> git clone fonts"
git clone --depth=1 `cat $ENV_DIR/FONTS_GIT_URL` fonts
rm -rf fonts/.git
