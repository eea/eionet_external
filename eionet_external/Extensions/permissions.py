from AccessControl import getSecurityManager

def checkPermissionViewManagementScreens(context):
    return getSecurityManager().checkPermission('View mamagement screens', context)
