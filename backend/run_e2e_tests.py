import unittest
import os
import shutil
import time
from command_router import execute_intent, get_user_profile

class TestMaverikE2E(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = os.path.join(get_user_profile(), "Desktop", "maverik_test_dir")
        self.test_file = os.path.join(self.test_dir, "test_file.txt")
        # Ensure clean state
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_file_operations(self):
        print("\n--- Testing File Operations ---")
        # Create Folder
        res = execute_intent("create_folder", {"path": self.test_dir})
        self.assertTrue(res.success)
        self.assertTrue(os.path.exists(self.test_dir))
        
        # Create File
        res = execute_intent("create_file", {"path": self.test_file, "content": "Hello E2E"})
        self.assertTrue(res.success)
        self.assertTrue(os.path.exists(self.test_file))
        
        # Read File
        res = execute_intent("read_file", {"path": self.test_file})
        self.assertTrue(res.success)
        self.assertIn("Hello E2E", res.details)
        
        # Rename File
        new_file = os.path.join(self.test_dir, "renamed.txt")
        res = execute_intent("rename_file", {"old_name": self.test_file, "new_name": new_file})
        self.assertTrue(res.success)
        self.assertTrue(os.path.exists(new_file))
        
        # Delete File
        res = execute_intent("delete_file", {"path": new_file, "confirmed": True})
        self.assertTrue(res.success)
        self.assertFalse(os.path.exists(new_file))
        
        # Delete Folder
        res = execute_intent("delete_folder", {"path": self.test_dir, "confirmed": True})
        self.assertTrue(res.success)
        self.assertFalse(os.path.exists(self.test_dir))

    def test_system_info(self):
        print("\n--- Testing System Info ---")
        from system_monitor import get_system_stats
        stats = get_system_stats()
        self.assertIn("cpu", stats)
        self.assertIn("ram", stats)
        self.assertIn("battery", stats)
        
    def test_time_date(self):
        print("\n--- Testing Time & Date ---")
        res1 = execute_intent("get_time", {})
        self.assertTrue(res1.success)
        
        res2 = execute_intent("get_date", {})
        self.assertTrue(res2.success)

    def test_clipboard(self):
        print("\n--- Testing Clipboard ---")
        res = execute_intent("clipboard_action", {"action": "copy", "content": "Automated Test String"})
        self.assertTrue(res.success)
        
        res2 = execute_intent("clipboard_action", {"action": "show"})
        self.assertTrue(res2.success)
        self.assertEqual(res2.details, "Automated Test String")

if __name__ == '__main__':
    unittest.main()
