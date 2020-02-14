from __future__ import absolute_import
from AccessControl import getSecurityManager

def checkPermissionViewManagementScreens(context):
    return getSecurityManager().checkPermission('View mamagement screens', context)
