#!/bin/sh

OUT_FILE="kubewatcher.yaml"
rm -f $OUT_FILE

echo "Creating single yaml manifest $OUT_FILE"

echo "# Custom Resource definitions" >> $OUT_FILE
cat kubewatcher-crds.yaml >> $OUT_FILE
echo "---" >> $OUT_FILE
echo >> $OUT_FILE

echo "# Service Accounts" >> $OUT_FILE
cat kubewatcher-sa.yaml >> $OUT_FILE
echo "---" >> $OUT_FILE
echo >> $OUT_FILE

echo "# RBAC Roles" >> $OUT_FILE
cat kubewatcher-role.yaml >> $OUT_FILE
echo "---" >> $OUT_FILE
echo >> $OUT_FILE

echo "# RBAC Role Bindings" >> $OUT_FILE
cat kubewatcher-rb.yaml >> $OUT_FILE
echo "---" >> $OUT_FILE
echo >> $OUT_FILE

echo "# Custom Resource Empty Instances" >> $OUT_FILE
cat kubewatcher-crins.yaml >> $OUT_FILE
echo "---" >> $OUT_FILE
echo >> $OUT_FILE

echo "# Registry Polling Cronjob" >> $OUT_FILE
cat kubewatcher-regpoll.yaml >> $OUT_FILE
echo "---" >> $OUT_FILE
echo >> $OUT_FILE

echo "# Main Deployment & Image Watcher" >> $OUT_FILE
cat kubewatcher-watcher.yaml >> $OUT_FILE
echo "---" >> $OUT_FILE
echo >> $OUT_FILE

echo "Done."
