import os

# Because guild ID is in int instead of string
guild = int(os.environ["BS_MOTD_GUILD"])
active_channel = int(os.environ["BS_MOTD_ACTIVE_CHANNEL"])
archived_channel = int(os.environ["BS_MOTD_ARCHIVED_CHANNEL"])
test_channel = int(os.environ["BS_MOTD_TEST_CHANNEL"])
