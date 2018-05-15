filename="ci-report-`date +\%d-\%m-\%Y`.html"
cp /root/poss-ci.github.io/index.html /root/poss-ci.github.io/archives/$filename
eval $(ssh-agent -s)
ssh-add ~/.ssh/id_rsa1
cd /root/poss-ci.github.io
git add archives/*
git commit -m "reporthistory-`date +\%Y-\%m-\%d-\%H:\%M`"
git push origin master
python fileviewer.py
git add archives.html
git commit -m "report archive viewer"
git push origin master
