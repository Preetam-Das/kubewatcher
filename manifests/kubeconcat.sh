#!/bin/sh

OUT_INSTALL_FILE="kubewatcher-install.yaml"
OUT_UNINSTALL_FILE="kubewatcher-uninstall.yaml"
rm -f $OUT_INSTALL_FILE
rm -f $OUT_UNINSTALL_FILE

echo "Creating single yaml manifest installer $OUT_INSTALL_FILE"

echo "# Custom Resource definitions" >> $OUT_INSTALL_FILE
cat kubewatcher-crds.yaml >> $OUT_INSTALL_FILE
echo "---" >> $OUT_INSTALL_FILE
echo >> $OUT_INSTALL_FILE

echo "# Service Accounts" >> $OUT_INSTALL_FILE
cat kubewatcher-sa.yaml >> $OUT_INSTALL_FILE
echo "---" >> $OUT_INSTALL_FILE
echo >> $OUT_INSTALL_FILE

echo "# RBAC Roles" >> $OUT_INSTALL_FILE
cat kubewatcher-role.yaml >> $OUT_INSTALL_FILE
echo "---" >> $OUT_INSTALL_FILE
echo >> $OUT_INSTALL_FILE

echo "# RBAC Role Bindings" >> $OUT_INSTALL_FILE
cat kubewatcher-rb.yaml >> $OUT_INSTALL_FILE
echo "---" >> $OUT_INSTALL_FILE
echo >> $OUT_INSTALL_FILE

echo "# Custom Resource Empty Instances" >> $OUT_INSTALL_FILE
cat kubewatcher-crins.yaml >> $OUT_INSTALL_FILE
echo "---" >> $OUT_INSTALL_FILE
echo >> $OUT_INSTALL_FILE

echo "# Registry Polling Cronjob" >> $OUT_INSTALL_FILE
cat kubewatcher-regpoll.yaml >> $OUT_INSTALL_FILE
echo "---" >> $OUT_INSTALL_FILE
echo >> $OUT_INSTALL_FILE

echo "# Main Deployment & Image Watcher" >> $OUT_INSTALL_FILE
cat kubewatcher-watcher.yaml >> $OUT_INSTALL_FILE
echo "---" >> $OUT_INSTALL_FILE
echo >> $OUT_INSTALL_FILE

echo "Creating single yaml manifest uninstaller $OUT_UNINSTALL_FILE"

echo "# Main Deployment & Image Watcher" >> $OUT_UNINSTALL_FILE
cat kubewatcher-watcher.yaml >> $OUT_UNINSTALL_FILE
echo "---" >> $OUT_UNINSTALL_FILE
echo >> $OUT_UNINSTALL_FILE

echo "# Registry Polling Cronjob" >> $OUT_UNINSTALL_FILE
cat kubewatcher-regpoll.yaml >> $OUT_UNINSTALL_FILE
echo "---" >> $OUT_UNINSTALL_FILE
echo >> $OUT_UNINSTALL_FILE

echo "# Custom Resource Empty Instances" >> $OUT_UNINSTALL_FILE
cat kubewatcher-crins.yaml >> $OUT_UNINSTALL_FILE
echo "---" >> $OUT_UNINSTALL_FILE
echo >> $OUT_UNINSTALL_FILE

echo "# RBAC Role Bindings" >> $OUT_UNINSTALL_FILE
cat kubewatcher-rb.yaml >> $OUT_UNINSTALL_FILE
echo "---" >> $OUT_UNINSTALL_FILE
echo >> $OUT_UNINSTALL_FILE

echo "# RBAC Roles" >> $OUT_UNINSTALL_FILE
cat kubewatcher-role.yaml >> $OUT_UNINSTALL_FILE
echo "---" >> $OUT_UNINSTALL_FILE
echo >> $OUT_UNINSTALL_FILE

echo "# Service Accounts" >> $OUT_UNINSTALL_FILE
cat kubewatcher-sa.yaml >> $OUT_UNINSTALL_FILE
echo "---" >> $OUT_UNINSTALL_FILE
echo >> $OUT_UNINSTALL_FILE

echo "# Custom Resource definitions" >> $OUT_UNINSTALL_FILE
cat kubewatcher-crds.yaml >> $OUT_UNINSTALL_FILE
echo "---" >> $OUT_UNINSTALL_FILE
echo >> $OUT_UNINSTALL_FILE

echo "Done."
