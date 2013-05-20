rm foodfor.tar.gz
tar czvf foodfor.tar.gz foodfor/
sftp -i ~/.ssh/BenderCI.pem ec2-user@ec2-50-16-131-215.compute-1.amazonaws.com << ! 
    put foodfor.tar.gz
!
echo "after sftp"
ssh -i ~/.ssh/BenderCI.pem ec2-user@ec2-50-16-131-215.compute-1.amazonaws.com 'bash -s' < run_on_ec2.sh
rm -rf foodfor.tar.gz
