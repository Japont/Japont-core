echo "-----> git clone fonts"
git clone \
    --depth 1 --single-branch \
    -b ${FONTS_GIT_BRANCH:-master} \
    $FONTS_GIT_URL fonts
rm -rf fonts/.git
