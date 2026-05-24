from enum import Enum
from typing import List

class PermissionTier(Enum):
    SAFE = "SAFE"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"

class ActionPermissionModel:
    def __init__(self):
        print("[Permissions] Initializing Action Permission Model")
        self.rules = {
            "navigate": PermissionTier.SAFE,
            "read": PermissionTier.SAFE,
            "type_search": PermissionTier.SAFE,
            "form_submit": PermissionTier.REVIEW,
            "file_upload": PermissionTier.REVIEW,
            "payment": PermissionTier.BLOCK,
            "change_password": PermissionTier.BLOCK
        }

    def evaluate_action(self, action: str, user_permissions: List[str]) -> bool:
        tier = self.rules.get(action, PermissionTier.REVIEW)

        if tier == PermissionTier.SAFE:
            return True
        elif tier == PermissionTier.REVIEW:
            print(f"[Permissions] Action '{action}' requires user REVIEW.")
            return action in user_permissions
        elif tier == PermissionTier.BLOCK:
            print(f"[Permissions] Action '{action}' is BLOCKED by default policy.")
            return False

        return False