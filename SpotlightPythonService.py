import sys
import os
import uuid
import logging
from AppKit import NSApplication, NSObject
from UniformTypeIdentifiers import UTTypeUTF8PlainText
from CoreSpotlight import (
    CSSearchableIndex,
    CSSearchableItem,
    CSSearchableItemAttributeSet,
)


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


logging.basicConfig(
    # <replace with an absolute path to access logs filename="/path/to/log" >,
    format="[%(asctime)s] [%(threadName)s:%(thread)d] [%(levelname)s] %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

data = [
    {
        "title": "Title 1",
        "display_name": "Advanced Stack Item 1",
        "content": "Sample content 1",
    },
    {
        "title": "Title 2",
        "display_name": "Advanced Stack Item 2",
        "content": "Sample content 2",
    },
    {
        "title": "Title 3",
        "display_name": "Advanced Stack Item 3",
        "content": "Sample content 3",
    },
    {
        "title": "Title 4",
        "display_name": "Advanced Stack Item 4",
        "content": "Sample content 4",
    },
    {
        "title": "Title 5",
        "display_name": "Advanced Stack Item 5",
        "content": "Sample content 5",
    },
]

with open(resource_path("logo.png"), "rb") as file:
    thumbnail_data = file.read()


def index_completion_handler(*args, **kwargs):
    logger.info(f"Indexed completion handler called - {args} - {kwargs}")


def purge_completion_handler(*args, **kwargs):
    logger.info(f"Purge completion handler called - {args} - {kwargs}")


def purge_everything():
    index = CSSearchableIndex.defaultSearchableIndex()
    index.deleteSearchableItemsWithDomainIdentifiers_completionHandler_(
        ["com.advanced-stack.app"], None
    )


def purge_searchable_item(item_id):
    index = CSSearchableIndex.defaultSearchableIndex()
    index.deleteSearchableItemsWithIdentifiers_completionHandler_(
        [item_id], purge_completion_handler
    )


def make_searchable_item(title, display_name, content):
    attribute_set = CSSearchableItemAttributeSet.alloc().initWithContentType_(
        UTTypeUTF8PlainText
    )

    attribute_set.setTitle_(title)
    attribute_set.setDisplayName_(display_name)
    attribute_set.setContentDescription_(content)
    attribute_set.setThumbnailData_(thumbnail_data)

    searchable_item = CSSearchableItem.alloc()
    searchable_item.initWithUniqueIdentifier_domainIdentifier_attributeSet_(
        uuid.uuid4().hex,
        "com.advanced-stack.app",
        attribute_set,
    )

    return searchable_item


def register_searchable_item(item):
    index = CSSearchableIndex.defaultSearchableIndex()
    index.indexSearchableItems_completionHandler_(
        [item], index_completion_handler
    )


class AppDelegate(NSObject):
    def applicationWillFinishLaunching_(self, notification):
        logger.info("Delegate: WillFinishLaunching -->")

        for item in data:
            searchable_item = make_searchable_item(**item)
            register_searchable_item(searchable_item)

        logger.info("WillFinishLaunching -- |")
        return True

    def applicationDidFinishLaunching_(self, notification):
        logger.info("Delegate: DidFinishLaunching -->")

        logger.info("DidFinishLaunching -- |")
        return

    def applicationWillTerminate_(self, notification):
        logger.info("Delegate: WillTerminate -->")

        purge_everything()

        logger.info("WillTerminate -- |")
        return True

    def application_continueUserActivity_restorationHandler_(
        self, application, userActivity, restorationHandler
    ):
        logger.info(f"received {userActivity.activityType()}")

        if userActivity.activityType() == "com.apple.corespotlightitem":
            userinfo = userActivity.userInfo()
            identifier = userinfo.get("kCSSearchableItemActivityIdentifier")
            query = userinfo.get("kCSSearchQueryString")
            item = userinfo.get("kCSSearchableItemActivityIdentifier")
            item_type = userinfo.get("kCSSearchableItemActionType")
            cont_type = userinfo.get("kCSQueryContinuationActionType")

            logger.info(
                "\n".join(
                    (
                        f"identifier:{identifier}",
                        f"query:{query}",
                        f"item:{item}",
                        f"item_type:{item_type}",
                        f"type:{cont_type}",
                    )
                )
            )
            return True


logger.info("Starting...")

app = NSApplication.sharedApplication()
delegate = AppDelegate.alloc().init()
app.setDelegate_(delegate)

app.run()
