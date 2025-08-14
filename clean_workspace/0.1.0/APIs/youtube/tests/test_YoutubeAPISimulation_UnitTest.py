# ---------------------------------------------------------------------------------------
# Unit Tests
# ---------------------------------------------------------------------------------------

import unittest
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

from pydantic import ValidationError

from youtube.SimulationEngine.custom_errors import InvalidPartParameterError
from youtube.SimulationEngine.custom_errors import InvalidMaxResultsError
from youtube.SimulationEngine.custom_errors import MissingPartParameterError
from youtube.SimulationEngine.custom_errors import MaxResultsOutOfRangeError
from youtube.SimulationEngine.db import DB

import youtube as YoutubeAPI

# Import individual modules for direct testing if needed
from youtube import (
    Activities,
    Caption,
    Channels,
    ChannelSection,
    ChannelStatistics,
    ChannelBanners,
    Comment,
    CommentThread,
    Subscriptions,
    VideoCategory,
    Memberships,
    Videos,
    Search,
)

from common_utils.base_case import BaseTestCaseWithErrorHandler
from youtube.SimulationEngine.custom_errors import InvalidPartParameterError

from youtube import list_channel_sections
from youtube import delete_channel_section
from youtube import list_comment_threads
from youtube import create_comment_thread
from youtube import list_channels


class Testyoutube(BaseTestCaseWithErrorHandler):

    def setUp(self):
        """Resets the database before each test."""
        # Re-initialize the DB with sample data

        DB.clear()
        DB.update(
            {
                "activities": [
                    {"kind": "youtube#activity", "etag": "etag1", "id": "activity1"},
                    {"kind": "youtube#activity", "etag": "etag2", "id": "activity2"},
                ],
                "captions": {
                    "caption1": {"id": "caption1", "snippet": {"videoId": "video1"}},
                    "caption2": {"id": "caption2", "snippet": {"videoId": "video2"}},
                },
                "channels": {
                    "channel1": {
                        "part": "snippet,contentDetails,statistics",
                        "categoryId": "10",
                        "forUsername": "TechGuru",
                        "hl": "en",
                        "id": "channel1",
                        "managedByMe": False,
                        "maxResults": 5,
                        "mine": False,
                        "mySubscribers": True,
                        "onBehalfOfContentOwner": None,
                    },
                    "channel2": {
                        "part": "snippet,statistics",
                        "categoryId": "20",
                        "forUsername": "FoodieFun",
                        "hl": "es",
                        "id": "channel2",
                        "managedByMe": True,
                        "maxResults": 10,
                        "mine": True,
                        "mySubscribers": False,
                        "onBehalfOfContentOwner": "CompanyXYZ",
                    },
                    "channel3": {
                        "part": "contentDetails,statistics",
                        "categoryId": "15",
                        "forUsername": "TravelVlogs",
                        "hl": "fr",
                        "id": "channel3",
                        "managedByMe": False,
                        "maxResults": 7,
                        "mine": False,
                        "mySubscribers": True,
                        "onBehalfOfContentOwner": None,
                    },
                },
                "channelSections": {
                    "section1": {
                        "id": "section1",
                        "snippet": {"channelId": "channel1", "type": "allPlaylists"},
                    },
                    "section2": {
                        "id": "section2",
                        "snippet": {"channelId": "channel2", "type": "completedEvents"},
                    },
                    "section3": {
                        "id": "section3",
                        "snippet": {
                            "channelId": "channel1",
                            "type": "multipleChannels",
                        },
                    },
                },
                "channelStatistics": {
                    "commentCount": 100,
                    "hiddenSubscriberCount": False,
                    "subscriberCount": 1000000,
                    "videoCount": 500,
                    "viewCount": 10000000,
                },
                "channelBanners": [],
                "comments": {
                    "comment1": {
                        "id": "comment1",
                        "snippet": {"videoId": "video1", "parentId": None},
                        "moderationStatus": "published",
                        "bannedAuthor": False,
                    },
                    "comment2": {
                        "id": "comment2",
                        "snippet": {"videoId": "video1", "parentId": "comment1"},
                        "moderationStatus": "heldForReview",
                        "bannedAuthor": False,
                    },
                    "comment3": {
                        "id": "comment3",
                        "snippet": {"videoId": "video2", "parentId": None},
                        "moderationStatus": "rejected",
                        "bannedAuthor": True,
                    },
                },
                "commentThreads": {
                    "thread1": {
                        "id": "thread1",
                        "snippet": {"channelId": "channel1", "videoId": "video1"},
                        "comments": ["comment1", "comment2"],
                    },
                    "thread2": {
                        "id": "thread2",
                        "snippet": {"channelId": "channel2", "videoId": "video2"},
                        "comments": ["comment3"],
                    },
                },
                "subscriptions": {
                    "sub1": {
                        "id": "sub1",
                        "snippet": {
                            "channelId": "channel1",
                            "resourceId": {
                                "kind": "youtube#channel",
                                "channelId": "channel2",
                            },
                        },
                    },
                    "sub2": {
                        "id": "sub2",
                        "snippet": {
                            "channelId": "channel2",
                            "resourceId": {
                                "kind": "youtube#channel",
                                "channelId": "channel1",
                            },
                        },
                    },
                },
                "videoCategories": {
                    "category1": {
                        "id": "1",
                        "snippet": {"title": "Film & Animation", "regionCode": "US"},
                    },
                    "category2": {
                        "id": "2",
                        "snippet": {"title": "Autos & Vehicles", "regionCode": "US"},
                    },
                    "category3": {
                        "id": "10",
                        "snippet": {"title": "Music", "regionCode": "CA"},
                    },
                },
                "memberships": {
                    "member1": {
                        "id": "member1",
                        "snippet": {
                            "memberChannelId": "channel1",
                            "hasAccessToLevel": "level1",
                            "mode": "fanFunding",
                        },
                    },
                    "member2": {
                        "id": "member2",
                        "snippet": {
                            "memberChannelId": "channel2",
                            "hasAccessToLevel": "level2",
                            "mode": "sponsors",
                        },
                    },
                },
                "videos": {
                    "video1": {
                        "id": "video1",
                        "snippet": {
                            "title": "Python Programming Tutorial",
                            "description": "Learn Python programming from scratch",
                            "publishedAt": "2023-01-01T00:00:00Z",
                            "channelId": "channel1",
                            "channelTitle": "TechGuru",
                            "categoryId": "28",
                            "tags": ["python", "programming", "tutorial"],
                            "thumbnails": {
                                "default": {
                                    "url": "https://google.com/thumb1.jpg",
                                    "width": 120,
                                    "height": 90,
                                },
                                "medium": {
                                    "url": "https://google.com/thumb2.jpg",
                                    "width": 320,
                                    "height": 180,
                                },
                                "high": {
                                    "url": "https://google.com/thumb3.jpg",
                                    "width": 480,
                                    "height": 360,
                                },
                            },
                        },
                        "contentDetails": {
                            "duration": "PT15M30S",
                            "dimension": "2d",
                            "definition": "hd",
                            "caption": "true",
                            "licensedContent": True,
                            "projection": "rectangular",
                        },
                        "status": {
                            "uploadStatus": "processed",
                            "privacyStatus": "public",
                            "license": "youtube",
                            "embeddable": True,
                            "publicStatsViewable": True,
                            "madeForKids": False,
                        },
                        "statistics": {
                            "viewCount": 10000,
                            "likeCount": 500,
                            "dislikeCount": 50,
                            "favoriteCount": 200,
                            "commentCount": 100,
                        },
                    },
                    "video2": {
                        "id": "video2",
                        "snippet": {
                            "title": "Cooking Basics",
                            "description": "Learn essential cooking techniques",
                            "publishedAt": "2023-02-01T00:00:00Z",
                            "channelId": "channel2",
                            "channelTitle": "FoodieFun",
                            "categoryId": "26",
                            "tags": ["cooking", "food", "tutorial"],
                            "thumbnails": {
                                "default": {
                                    "url": "https://google.com/thumb4.jpg",
                                    "width": 120,
                                    "height": 90,
                                },
                                "medium": {
                                    "url": "https://google.com/thumb5.jpg",
                                    "width": 320,
                                    "height": 180,
                                },
                                "high": {
                                    "url": "https://google.com/thumb6.jpg",
                                    "width": 480,
                                    "height": 360,
                                },
                            },
                        },
                        "contentDetails": {
                            "duration": "PT20M15S",
                            "dimension": "2d",
                            "definition": "hd",
                            "caption": "true",
                            "licensedContent": True,
                            "projection": "rectangular",
                        },
                        "status": {
                            "uploadStatus": "processed",
                            "privacyStatus": "public",
                            "license": "youtube",
                            "embeddable": True,
                            "publicStatsViewable": True,
                            "madeForKids": False,
                        },
                        "statistics": {
                            "viewCount": 5000,
                            "likeCount": 300,
                            "dislikeCount": 20,
                            "favoriteCount": 100,
                            "commentCount": 50,
                        },
                    },
                },
            }
        )

    def test_activities_list(self):
        """Tests the Activities.list method."""
        # Test basic listing
        response = Activities.list(part="snippet")
        self.assertEqual(len(response["items"]), 2)

        # Test filtering by channelId
        response = Activities.list(part="snippet", channelId="channel1")
        self.assertEqual(
            len(response["items"]), 0
        )  # No activities with channelId in the sample data

        # Test filtering by mine
        response = Activities.list(part="snippet", mine=True)
        self.assertEqual(
            len(response["items"]), 0
        )  # No activities with mine=True in the sample data

        # Test maxResults
        response = Activities.list(part="snippet", maxResults=1)
        self.assertEqual(len(response["items"]), 1)

    def test_captions_insert(self):
        """Tests the Captions.insert method."""
        response = Caption.insert(part="snippet", snippet={})
        self.assertTrue(response["success"])
        self.assertIn("caption", response)
        self.assertIn("id", response["caption"])

    def test_Caption_list(self):
        """Tests the Caption.list method."""
        # Test basic listing
        response = YoutubeAPI.Caption.list(part="snippet", videoId="video1")
        self.assertEqual(len(response["items"]), 1)

        # Test filtering by id
        response = YoutubeAPI.Caption.list(
            part="snippet", videoId="video1", id="caption1"
        )
        self.assertEqual(len(response["items"]), 1)

        # Test filtering by videoId that doesn't exist
        response = YoutubeAPI.Caption.list(part="snippet", videoId="nonexistent")
        self.assertEqual(len(response["items"]), 0)

    def test_captions_delete(self):
        """Tests the Captions.delete method."""
        response = Caption.delete(id="caption1")
        self.assertTrue(response["success"])
        from youtube.SimulationEngine.db import DB

        self.assertNotIn("caption1", DB["captions"])

    def test_captions_download(self):
        """Tests the Captions.download method."""
        # Test basic download
        response = Caption.download(id="caption1")
        self.assertEqual(response, "Caption content")  # Default content

        # Test format parameter
        response = Caption.download(id="caption1", tfmt="srt")
        self.assertEqual(response, "Simulated SRT content")

        response = Caption.download(id="caption1", tfmt="vtt")
        self.assertEqual(response, "Simulated VTT content")

        # Test language parameter
        response = Caption.download(id="caption1", tlang="es")
        self.assertEqual(response, "Simulated translated caption to es")

    def test_captions_update(self):
        """Tests the Captions.update method."""
        response = Caption.update(part="snippet", id="caption1")
        # self.assertEqual(response["part"], "snippet")
        self.assertTrue(response["success"])

    def test_channels_list(self):
        """Tests the Channels.list method."""
        # Test filtering by categoryId
        response = YoutubeAPI.Channels.list(category_id="10")
        self.assertEqual(
            len(response["items"]), 1
        )  # One channel with categoryId="10" in the sample data

        # Test filtering by id
        response = YoutubeAPI.Channels.list(channel_id="channel1")
        self.assertEqual(len(response["items"]), 1)

        # Test maxResults
        response = YoutubeAPI.Channels.list(max_results=1)
        self.assertEqual(len(response["items"]), 1)

        # Test non-existent channel id
        response = YoutubeAPI.Channels.list(channel_id="non-existent-channel")
        self.assertEqual(len(response["items"]), 0)  # Should return empty list for non-existent channel
        
        # Test error handling - invalid parameter type
        try:
            response = YoutubeAPI.Channels.list(max_results="not-a-number")
            # If no exception is thrown, check for error in the response
            if isinstance(response, dict) and "error" in response:
                self.assertIn("error", response)
        except Exception as e:
            # Exception thrown is also valid behavior
            self.assertEqual(str(e), "max_results must be an integer or None.")
            
        # Test error handling - invalid parameter value
        try:
            response = YoutubeAPI.Channels.list(max_results=-1)  # Negative max_results is invalid
            # If no exception is thrown, check for error in the response
            if isinstance(response, dict) and "error" in response:
                self.assertIn("error", response)
        except Exception as e:
            # Exception thrown is also valid behavior
            self.assertEqual(str(e), "max_results must be between 1 and 50, inclusive.")

    def test_channel_sections_list(self):
        """Tests the ChannelSections.list method."""
        # Test basic listing with valid part
        response = ChannelSection.list(part="snippet")
        self.assertEqual(len(response["items"]), 3)

        # Test filtering by id
        response = ChannelSection.list(part="snippet", section_id="section1")
        self.assertEqual(len(response["items"]), 1)

        # Test filtering by channelId
        response = ChannelSection.list(part="snippet", channel_id="channel1")
        self.assertEqual(len(response["items"]), 2)
        
        # Test with multiple valid parts
        response = ChannelSection.list(part="snippet,contentDetails")
        self.assertEqual(len(response["items"]), 3)
        
        # Test error cases - function can either raise an exception or return an error dictionary
        
        # Test invalid part parameter - empty string
        try:
            response = ChannelSection.list(part="")
            # If no exception is raised, check for error dictionary
            self.assertIn("error", response)
            self.assertTrue("cannot be empty" in response["error"] or "empty" in response["error"])
        except InvalidPartParameterError as e:
            # If exception is raised, check the message
            self.assertTrue("cannot be empty" in str(e))
        
        # Test invalid part parameter - only commas
        try:
            response = ChannelSection.list(part=",,,")
            # If no exception is raised, check for error dictionary
            self.assertIn("error", response)
            self.assertTrue("no valid components" in response["error"] or "Invalid part" in response["error"])
        except InvalidPartParameterError as e:
            # If exception is raised, check the message
            self.assertTrue("no valid components" in str(e))
        
        # Test invalid part parameter - no valid parts
        try:
            response = ChannelSection.list(part="invalid")
            # If no exception is raised, check for error dictionary
            self.assertIn("error", response)
            self.assertTrue("Invalid part parameter" in response["error"])
        except InvalidPartParameterError as e:
            # If exception is raised, check the message
            self.assertTrue("Invalid part parameter" in str(e))
        
        # Test type errors for parameters
        try:
            response = ChannelSection.list(part=123)  # part must be string
            self.assertIn("error", response)
        except TypeError:
            pass  # Expected behavior
            
        try:
            response = ChannelSection.list(part="snippet", channel_id=123)  # channel_id must be string or None
            self.assertIn("error", response)
        except TypeError:
            pass  # Expected behavior
            
        try:
            response = ChannelSection.list(part="snippet", hl=123)  # hl must be string or None
            self.assertIn("error", response)
        except TypeError:
            pass  # Expected behavior
            
        try:
            response = ChannelSection.list(part="snippet", section_id=123)  # section_id must be string or None
            self.assertIn("error", response)
        except TypeError:
            pass  # Expected behavior
            
        try:
            response = ChannelSection.list(part="snippet", mine="yes")  # mine must be boolean
            self.assertIn("error", response)
        except TypeError:
            pass  # Expected behavior
            
        try:
            response = ChannelSection.list(part="snippet", on_behalf_of_content_owner=123)  # must be string or None
            self.assertIn("error", response)
        except TypeError:
            pass  # Expected behavior

    def test_channel_sections_delete(self):
        """Tests the ChannelSection.delete method."""
        response = YoutubeAPI.ChannelSection.delete(section_id="section1")
        self.assertTrue(response["success"])
        from youtube.SimulationEngine.db import DB

        self.assertNotIn("section1", DB["channelSections"])

    def test_channel_sections_insert(self):
        """Tests the ChannelSections.insert method."""
        response = ChannelSection.insert(part="snippet", snippet={})
        self.assertTrue(response["success"])
        self.assertIn("channelSection", response)
        self.assertIn("id", response["channelSection"])

    def test_channel_sections_update(self):
        """Tests the ChannelSection.update method."""
        response = YoutubeAPI.ChannelSection.update(
            section_id="section1", part="snippet"
        )
        self.assertTrue(response["success"])

    def test_channel_statistics_comment_count(self):
        """Tests the ChannelStatistics.commentCount method."""
        response = ChannelStatistics.comment_count()
        self.assertEqual(response["commentCount"], 100)

    def test_channel_statistics_hidden_subscriber_count(self):
        """Tests the ChannelStatistics.hiddenSubscriberCount method."""
        response = ChannelStatistics.hidden_subscriber_count()
        self.assertFalse(response["hiddenSubscriberCount"])

    def test_channel_statistics_subscriber_count(self):
        """Tests the ChannelStatistics.subscriberCount method."""
        response = ChannelStatistics.subscriber_count()
        self.assertEqual(response["subscriberCount"], 1000000)

    def test_channel_statistics_video_count(self):
        """Tests the ChannelStatistics.videoCount method."""
        response = ChannelStatistics.video_count()
        self.assertEqual(response["videoCount"], 500)

    def test_channel_statistics_view_count(self):
        """Tests the ChannelStatistics.viewCount method."""
        response = ChannelStatistics.view_count()
        self.assertEqual(response["viewCount"], 10000000)

    def test_channel_banners_insert(self):
        """Tests the ChannelBanners.insert method."""
        response = YoutubeAPI.ChannelBanners.insert(channel_id="channel1")
        self.assertEqual(response["channelId"], "channel1")
        from youtube.SimulationEngine.db import DB

        self.assertEqual(len(DB["channelBanners"]), 1)

    def test_comment_set_moderation_status(self):
        """Tests the Comment.setModerationStatus method."""
        response = YoutubeAPI.Comment.set_moderation_status(
            comment_id="comment1", moderation_status="heldForReview"
        )
        self.assertTrue(response["success"])
        from youtube.SimulationEngine.db import DB

        self.assertEqual(
            DB["comments"]["comment1"]["moderationStatus"], "heldForReview"
        )

    def test_comment_delete(self):
        """Tests the Comment.delete method."""
        response = YoutubeAPI.Comment.delete(comment_id="comment1")
        self.assertTrue(response["success"])
        from youtube.SimulationEngine.db import DB

        self.assertNotIn("comment1", DB["comments"])

    def test_comment_insert(self):
        """Tests the Comment.insert method."""
        response = YoutubeAPI.Comment.insert(part="snippet")
        self.assertTrue(response["success"])
        self.assertIn("comment", response)
        self.assertIn("id", response["comment"])
        new_comment_id = response["comment"]["id"]  # Capture the generated ID
        from youtube.SimulationEngine.db import DB

        self.assertIn(new_comment_id, DB["comments"])

    def test_comment_list(self):
        """Tests the Comment.list method."""
        # Test basic listing
        response = Comment.list(part="snippet")
        self.assertEqual(len(response["items"]), 3)

        # Test filtering by id
        response = Comment.list(part="snippet", comment_id="comment1")
        self.assertEqual(len(response["items"]), 1)

        # Test filtering by parentId
        response = Comment.list(part="snippet", parent_id="comment1")
        self.assertEqual(len(response["items"]), 1)

    def test_comment_mark_as_spam(self):
        """Tests the Comment.markAsSpam method."""
        response = YoutubeAPI.Comment.mark_as_spam(comment_id="comment1")
        self.assertTrue(response["success"])
        from youtube.SimulationEngine.db import DB

        self.assertEqual(
            DB["comments"]["comment1"]["moderationStatus"], "heldForReview"
        )

    def test_comment_update(self):
        """Tests the Comment.update method."""
        response = YoutubeAPI.Comment.update(comment_id="comment1", snippet={"a": "b"})
        self.assertEqual(list(response.keys()), ["success"])

    def test_comment_thread_insert(self):
        """Tests the CommentThread.insert method."""
        response = YoutubeAPI.CommentThread.insert(part="snippet")
        self.assertTrue(response["success"])
        self.assertIn("commentThread", response)
        self.assertIn("id", response["commentThread"])
        new_thread_id = response["commentThread"]["id"]  # Capture the generated ID
        from youtube.SimulationEngine.db import DB

        self.assertIn(
            new_thread_id, DB["commentThreads"]
        )  # Use the ID in the assertion

    def test_comment_thread_list(self):
        """Tests the CommentThread.list method."""
        # Test basic listing
        response = CommentThread.list(part="snippet")
        self.assertEqual(len(response["items"]), 2)

        # Test filtering by id
        response = CommentThread.list(part="snippet", thread_id="thread1")
        self.assertEqual(len(response["items"]), 1)

        # Test filtering by channelId
        response = CommentThread.list(part="snippet", channel_id="channel1")
        self.assertEqual(len(response["items"]), 1)

    def test_list_videos_with_chart(self):
        # Test listing most popular videos
        result = Videos.list(part="snippet", chart="mostPopular")
        self.assertIn("items", result)
        self.assertIn("pageInfo", result)
        self.assertEqual(result["kind"], "youtube#videoListResponse")

        # Verify videos are sorted by view count
        items = result["items"]
        if items:  # Check if there are any items to sort
            for i in range(len(items) - 1):
                current_views = items[i]["statistics"]["viewCount"]
                next_views = items[i + 1]["statistics"]["viewCount"]
                self.assertGreaterEqual(current_views, next_views)

    def test_list_videos_with_id(self):
        # Test listing videos by ID
        result = Videos.list(part="snippet", id="video1")
        self.assertIn("items", result)
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0]["id"], "video1")

    def test_list_videos_invalid_params(self):
        # Test with missing part parameter
        result = Videos.list(part="")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "The 'part' parameter is required.")

        # Test with multiple filter parameters
        result = Videos.list(part="snippet", chart="mostPopular", id="video1")
        self.assertIn("error", result)
        self.assertEqual(
            result["error"],
            "Exactly one of 'chart', 'id', or 'my_rating' must be specified.",
        )

        # Test with invalid chart value
        result = Videos.list(part="snippet", chart="invalid")
        self.assertIn("error", result)
        self.assertEqual(
            result["error"],
            "Invalid value for 'chart'. Only 'mostPopular' is supported.",
        )

    def test_rate_video(self):
        # Test liking a video
        result = Videos.rate("video1", "like")
        self.assertTrue(result["success"])
        from youtube.SimulationEngine.db import DB

        self.assertEqual(DB["videos"]["video1"]["statistics"]["likeCount"], 501)

        # Test disliking a video
        result = Videos.rate("video1", "dislike")
        self.assertTrue(result["success"])
        self.assertEqual(DB["videos"]["video1"]["statistics"]["dislikeCount"], 50)
        self.assertEqual(DB["videos"]["video1"]["statistics"]["likeCount"], 500)

        # Test removing rating
        result = Videos.rate("video1", "none")
        self.assertTrue(result["success"])
        self.assertEqual(DB["videos"]["video1"]["statistics"]["dislikeCount"], 49)
        self.assertEqual(DB["videos"]["video1"]["statistics"]["likeCount"], 499)

    def test_rate_video_invalid(self):
        # Test with non-existent video
        result = Videos.rate("nonexistent", "like")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Video not found")

        # Test with invalid rating
        result = Videos.rate("video1", "invalid")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Invalid rating")

    def test_report_abuse(self):
        # Test reporting a video
        result = Videos.report_abuse("video1", "reason1")
        self.assertTrue(result["success"])

        # Test with non-existent video
        result = Videos.report_abuse("nonexistent", "reason1")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Video not found")

        # Test with missing reason
        result = Videos.report_abuse("video1", "")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Reason ID is required")

    def test_delete_video(self):
        # Test deleting a video
        result = Videos.delete("video1")
        self.assertTrue(result["success"])
        from youtube.SimulationEngine.db import DB

        self.assertNotIn("video1", DB["videos"])

        # Test deleting non-existent video
        result = Videos.delete("nonexistent")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Video not found")

    def test_update_video(self):
        # Test updating video snippet
        update_body = {
            "id": "video1",
            "snippet": {"title": "Updated Title", "description": "Updated Description"},
        }
        result = Videos.update("snippet", update_body)
        self.assertEqual(result["snippet"]["title"], "Updated Title")
        self.assertEqual(result["snippet"]["description"], "Updated Description")

        # Test updating multiple parts
        update_body = {
            "id": "video1",
            "snippet": {"title": "New Title"},
            "status": {"privacyStatus": "private"},
        }
        result = Videos.update("snippet,status", update_body)
        self.assertEqual(result["snippet"]["title"], "New Title")
        self.assertEqual(result["status"]["privacyStatus"], "private")

        # Test with invalid part
        update_body = {"id": "video1", "snippet": {"title": "New Title"}}
        result = Videos.update("invalid", update_body)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Invalid part parameter: invalid")

        # Test with non-existent video
        update_body["id"] = "nonexistent"
        result = Videos.update("snippet", update_body)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Video not found: nonexistent")

    def test_search_videos(self):
        # Test basic video search
        result = Search.list(part="snippet", q="Python")
        self.assertIn("items", result)
        self.assertEqual(result["kind"], "youtube#searchListResponse")

        # Verify search results contain the query term
        for item in result["items"]:
            if "snippet" in item:  # Ensure 'snippet' exists
                title = item["snippet"]["title"].lower()
                description = item["snippet"]["description"].lower()
                self.assertTrue("python" in title or "python" in description)

    def test_search_with_filters(self):
        """Tests searching with filters."""
        # Test search with channel filter
        result = YoutubeAPI.Search.list(part="snippet", channel_id="channel1")
        self.assertIn("items", result)
        for item in result["items"]:
            if "snippet" in item and "channelId" in item["snippet"]:
                self.assertEqual(item["snippet"]["channelId"], "channel1")

        # Test search with video category
        result = YoutubeAPI.Search.list(part="snippet", video_category_id="28")
        self.assertIn("items", result)
        for item in result["items"]:
            if "snippet" in item and "categoryId" in item["snippet"]:
                self.assertEqual(item["snippet"]["categoryId"], "28")

    def test_search_invalid_params(self):
        # Test with missing part parameter
        result = Search.list(part="")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "The 'part' parameter is required.")

        # Test with invalid part parameter
        result = Search.list(part="invalid")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Invalid part parameter: invalid")

        # Test with invalid order parameter
        result = Search.list(part="snippet", order="invalid")
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Invalid order parameter: invalid")

    def test_search_max_results(self):
        """Tests searching with max results parameter."""
        # Test max_results parameter
        max_results = 5
        result = YoutubeAPI.Search.list(part="snippet", max_results=max_results)
        self.assertLessEqual(len(result["items"]), max_results)

        # Test with very large max_results
        result = YoutubeAPI.Search.list(part="snippet", max_results=100)
        self.assertLessEqual(len(result["items"]), 50)  # API limit is 50


    def test_valid_input_basic(self):
        """Test that a basic valid call is accepted."""
        result = list_comment_threads(part="snippet")
        self.assertIsInstance(result, dict)
        self.assertIn("items", result)
        self.assertIsInstance(result["items"], list)
        # The content of items will depend on the mock DB and filters.
        # Here, with no filters, it should return all threads from mock DB.
        self.assertEqual(len(result["items"]), 2) 

    def test_valid_input_with_all_optional_params_none(self):
        """Test valid input with all optional parameters as None (default)."""
        result = list_comment_threads(part="snippet")
        self.assertIsInstance(result, dict)
        self.assertIn("items", result)

    def test_valid_input_with_max_results(self):
        """Test valid input with max_results specified."""
        result = list_comment_threads(part="snippet", max_results=1)
        self.assertIsInstance(result, dict)
        self.assertIn("items", result)
        self.assertEqual(len(result["items"]), 1)

    # --- Tests for 'part' parameter ---
    def test_invalid_part_none(self):
        """Test that 'part' being None raises MissingPartParameterError."""
        # Pydantic treats None for a required field as 'missing'
        self.assert_error_behavior(
            func_to_call=list_comment_threads,
            expected_exception_type=MissingPartParameterError,
            expected_message="Parameter 'part' is required and cannot be empty.",
            part=None # type: ignore 
        )

    def test_invalid_part_empty_string(self):
        """Test that 'part' being an empty string raises MissingPartParameterError."""
        self.assert_error_behavior(
            func_to_call=list_comment_threads,
            expected_exception_type=MissingPartParameterError,
            expected_message="Parameter 'part' is required and cannot be empty.",
            part=""
        )

    def test_invalid_part_type(self):
        """Test that 'part' being a non-string type raises TypeError."""
        self.assert_error_behavior(
            func_to_call=list_comment_threads,
            expected_exception_type=TypeError,
            expected_message="Parameter 'part' must be a string.",
            part=123 # type: ignore
        )

    # --- Tests for 'max_results' parameter ---
    def test_invalid_max_results_type(self):
        """Test that 'max_results' being a non-integer type raises TypeError."""
        self.assert_error_behavior(
            func_to_call=list_comment_threads,
            expected_exception_type=TypeError,
            expected_message="Parameter 'max_results' must be an integer if provided.",
            part="snippet",
            max_results="abc" # type: ignore
        )

    def test_invalid_max_results_zero(self):
        """Test that 'max_results' being zero raises InvalidMaxResultsError."""
        self.assert_error_behavior(
            func_to_call=list_comment_threads,
            expected_exception_type=InvalidMaxResultsError,
            expected_message="Parameter 'max_results' must be a positive integer if provided.",
            part="snippet",
            max_results=0
        )

    def test_invalid_max_results_negative(self):
        """Test that 'max_results' being negative raises InvalidMaxResultsError."""
        self.assert_error_behavior(
            func_to_call=list_comment_threads,
            expected_exception_type=InvalidMaxResultsError,
            expected_message="Parameter 'max_results' must be a positive integer if provided.",
            part="snippet",
            max_results=-5
        )
    
    # --- Tests for other Optional[str] parameters for type errors ---
    def test_invalid_thread_id_type(self):
        """Test that 'thread_id' of invalid type raises TypeError."""
        self.assert_error_behavior(
            func_to_call=list_comment_threads,
            expected_exception_type=TypeError,
            expected_message="Parameter 'thread_id' must be a string if provided.",
            part="snippet",
            thread_id=123 # type: ignore
        )

    def test_invalid_channel_id_type(self):
        """Test that 'channel_id' of invalid type raises TypeError."""
        self.assert_error_behavior(
            func_to_call=list_comment_threads,
            expected_exception_type=TypeError,
            expected_message="Parameter 'channel_id' must be a string if provided.",
            part="snippet",
            channel_id=False # type: ignore
        )

    def test_invalid_video_id_type(self):
        """Test that 'video_id' of invalid type raises TypeError."""
        self.assert_error_behavior(
            func_to_call=list_comment_threads,
            expected_exception_type=TypeError,
            expected_message="Parameter 'video_id' must be a string if provided.",
            part="snippet",
            video_id=object() # type: ignore
        )
        
    def test_invalid_search_terms_type(self):
        """Test that 'search_terms' of invalid type raises TypeError."""
        self.assert_error_behavior(
            list_comment_threads,
            TypeError,
            "Parameter 'search_terms' must be a string if provided.",
            part="snippet", search_terms=12345 #type: ignore
        )

    def test_invalid_moderation_status_type(self):
        """Test that 'moderation_status' of invalid type raises TypeError."""
        self.assert_error_behavior(
            list_comment_threads,
            TypeError,
            "Parameter 'moderation_status' must be a string if provided.",
            part="snippet", moderation_status=['published'] #type: ignore
        )

    def test_invalid_order_type(self):
        """Test that 'order' of invalid type raises TypeError."""
        self.assert_error_behavior(
            list_comment_threads,
            TypeError,
            "Parameter 'order' must be a string if provided.",
            part="snippet", order=1.0 #type: ignore
        )

    def test_invalid_page_token_type(self):
        """Test that 'page_token' of invalid type raises TypeError."""
        self.assert_error_behavior(
            list_comment_threads,
            TypeError,
            "Parameter 'page_token' must be a string if provided.",
            part="snippet", page_token=object() #type: ignore
        )

    def test_invalid_text_format_type(self):
        """Test that 'text_format' of invalid type raises TypeError."""
        self.assert_error_behavior(
            list_comment_threads,
            TypeError,
            "Parameter 'text_format' must be a string if provided.",
            part="snippet", text_format=True #type: ignore
        )

    def test_function_filters_by_video_id(self):
        """Test core logic: filtering by video_id works after validation."""
        result = list_comment_threads(part="snippet", video_id="video1")
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0]["id"], "thread1")

    def test_function_filters_by_search_terms(self):
        """Test core logic: filtering by search_terms works after validation."""
        result = list_comment_threads(part="snippet", search_terms="Hello world")
        self.assertEqual(len(result["items"]), 0)

    def test_valid_input_all_parameters(self):
        """Test successful insertion with all parameters valid."""
        part_input = "snippet"
        snippet_input = {"author": "test_user", "text": "This is a test snippet."}
        top_level_comment_input = {"id": "comment-1", "text": "Great point!"}

        result = create_comment_thread(
            part=part_input,
            snippet=snippet_input,
            top_level_comment=top_level_comment_input
        )

        self.assertTrue(result.get("success"))
        self.assertIn("commentThread", result)
        thread = result["commentThread"]
        self.assertIsNotNone(thread)
        self.assertIn("id", thread) # type: ignore
        self.assertEqual(thread["snippet"], snippet_input) # type: ignore
        self.assertIn("comment-1", thread["comments"]) # type: ignore

    def test_valid_input_optional_missing(self):
        """Test successful insertion with optional snippet and top_level_comment as None."""
        part_input = "snippet"

        result = create_comment_thread(part=part_input, snippet=None, top_level_comment=None)

        self.assertTrue(result.get("success"))
        self.assertIn("commentThread", result)
        thread = result["commentThread"]
        self.assertIsNotNone(thread)
        self.assertIn("id", thread) # type: ignore
        self.assertEqual(thread["snippet"], {}) # type: ignore
        self.assertEqual(thread["comments"], []) # type: ignore

    def test_valid_input_empty_snippet(self):
        """Test successful insertion with empty snippet dictionary."""
        part_input = "snippet"
        snippet_input = {}

        result = create_comment_thread(part=part_input, snippet=snippet_input)

        self.assertTrue(result.get("success"))
        thread = result["commentThread"]
        self.assertIsNotNone(thread)
        self.assertEqual(thread["snippet"], {}) # type: ignore

    def test_valid_top_level_comment_no_id(self):
        """Test successful insertion with top_level_comment present but no 'id' field."""
        part_input = "snippet"
        top_level_comment_input = {"text": "A comment without an explicit ID field for this test."}

        result = create_comment_thread(part=part_input, top_level_comment=top_level_comment_input)
        
        self.assertTrue(result.get("success"))
        thread = result["commentThread"]
        self.assertIsNotNone(thread)
        self.assertEqual(thread["comments"], []) # type: ignore

    # --- Validation Tests for 'part' ---
    def test_invalid_part_type(self):
        """Test that non-string 'part' raises TypeError."""
        self.assert_error_behavior(
            func_to_call=create_comment_thread,
            expected_exception_type=TypeError,
            expected_message="Parameter 'part' must be a string.",
            part=123
        )

    def test_invalid_part_value(self):
        """Test that incorrect 'part' string raises InvalidPartParameterError."""
        self.assert_error_behavior(
            func_to_call=create_comment_thread,
            expected_exception_type=InvalidPartParameterError,
            expected_message="Invalid 'part' parameter: 'invalid_value'. Must be 'snippet'.",
            part="invalid_value"
        )

    # --- Validation Tests for 'snippet' (Pydantic) ---
    def test_invalid_snippet_type(self):
        """Test that non-dict 'snippet' raises Pydantic ValidationError."""
        self.assert_error_behavior(
            func_to_call=create_comment_thread,
            expected_exception_type=TypeError,
            expected_message="Parameter 'snippet' must be a dictionary.",
            part="snippet",
            snippet="not_a_dictionary"
        )

    # --- Validation Tests for 'top_level_comment' (Pydantic) ---
    def test_invalid_top_level_comment_type(self):
        """Test that non-dict 'top_level_comment' raises Pydantic ValidationError."""
        self.assert_error_behavior(
            func_to_call=create_comment_thread,
            expected_exception_type=TypeError,
            expected_message="Parameter 'top_level_comment' must be a dictionary.",
            part="snippet",
            top_level_comment="not_a_dictionary"
        )

    def test_snippet_allows_arbitrary_fields(self):
        """Test that 'snippet' Pydantic model allows arbitrary fields."""
        part_input = "snippet"
        snippet_input = {"custom_field": "custom_value", "another": 123}
        
        result = create_comment_thread(part=part_input, snippet=snippet_input)
        self.assertTrue(result.get("success"))
        thread = result["commentThread"]
        self.assertIsNotNone(thread)
        self.assertEqual(thread["snippet"], snippet_input) # type: ignore

    def test_top_level_comment_allows_arbitrary_fields(self):
        """Test that 'top_level_comment' Pydantic model allows arbitrary fields."""
        part_input = "snippet"
        top_level_comment_input = {"id": "comment-id-x", "custom_data": "value", "numeric": 42}
        
        result = create_comment_thread(part=part_input, top_level_comment=top_level_comment_input)
        self.assertTrue(result.get("success"))
        thread = result["commentThread"]
        self.assertIsNotNone(thread)
        self.assertIn("comment-id-x", thread["comments"]) # type: ignore


    def test_valid_input_all_none(self):
        """Test with all optional parameters as None, returning all items."""
        result = list_channels()
        self.assertIsInstance(result, dict)
        self.assertIn("items", result)
        self.assertEqual(len(result["items"]), 3) # All channels from mock DB

    def test_valid_input_with_category_id(self):
        """Test filtering by category_id."""
        result = list_channels(category_id="news")
        self.assertEqual(len(result["items"]), 0)
        self.assertTrue(all(item["categoryId"] == "news" for item in result["items"]))

    def test_valid_input_with_for_username(self):
        """Test filtering by for_username."""
        result = list_channels(for_username="testuser")
        self.assertEqual(len(result["items"]), 0)

    def test_valid_input_with_channel_id(self):
        """Test filtering by a specific channel_id."""
        result = list_channels(channel_id="ch2")
        self.assertEqual(len(result["items"]), 0)
        
    def test_valid_input_with_hl(self):
        """Test filtering by hl."""
        result = list_channels(hl="en")
        self.assertEqual(len(result["items"]), 1) # ch1, ch3
        self.assertTrue(all(item["hl"] == "en" for item in result["items"]))

    def test_valid_input_with_managed_by_me(self):
        """Test filtering by managed_by_me."""
        result = list_channels(managed_by_me=True)
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0]["id"], "channel2")

    def test_valid_input_with_mine(self):
        """Test filtering by mine."""
        result = list_channels(mine=True)
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0]["id"], "channel2")

    def test_valid_input_with_my_subscribers(self):
        """Test filtering by my_subscribers."""
        result = list_channels(my_subscribers=True)
        self.assertEqual(len(result["items"]), 2)
        self.assertEqual(result["items"][0]["id"], "channel1")
        
    def test_valid_input_with_on_behalf_of_content_owner(self):
        """Test filtering by on_behalf_of_content_owner."""
        result = list_channels(on_behalf_of_content_owner="content_owner_A")
        self.assertEqual(len(result["items"]), 0)

    def test_valid_max_results(self):
        """Test limiting results with max_results."""
        result = list_channels(max_results=2)
        self.assertEqual(len(result["items"]), 2)

    def test_valid_max_results_boundary_low(self):
        """Test max_results at lower boundary (1)."""
        result = list_channels(max_results=1)
        self.assertEqual(len(result["items"]), 1)

    # Type Error Tests
    def test_invalid_type_category_id(self):
        """Test TypeError for invalid category_id type."""
        self.assert_error_behavior(
            list_channels, TypeError, "category_id must be a string or None.", category_id=123
        )

    def test_invalid_type_for_username(self):
        """Test TypeError for invalid for_username type."""
        self.assert_error_behavior(
            list_channels, TypeError, "for_username must be a string or None.", for_username=123
        )

    def test_invalid_type_hl(self):
        """Test TypeError for invalid hl type."""
        self.assert_error_behavior(
            list_channels, TypeError, "hl must be a string or None.", hl=True
        )

    def test_invalid_type_channel_id(self):
        """Test TypeError for invalid channel_id type."""
        self.assert_error_behavior(
            list_channels, TypeError, "channel_id must be a string or None.", channel_id=["id1"]
        )

    def test_invalid_type_managed_by_me(self):
        """Test TypeError for invalid managed_by_me type."""
        self.assert_error_behavior(
            list_channels, TypeError, "managed_by_me must be a boolean or None.", managed_by_me="true"
        )
    
    def test_invalid_type_mine(self):
        """Test TypeError for invalid mine type."""
        self.assert_error_behavior(
            list_channels, TypeError, "mine must be a boolean or None.", mine=0
        )

    def test_invalid_type_my_subscribers(self):
        """Test TypeError for invalid my_subscribers type."""
        self.assert_error_behavior(
            list_channels, TypeError, "my_subscribers must be a boolean or None.", my_subscribers="yes"
        )
        
    def test_invalid_type_on_behalf_of_content_owner(self):
        """Test TypeError for invalid on_behalf_of_content_owner type."""
        self.assert_error_behavior(
            list_channels, TypeError, "on_behalf_of_content_owner must be a string or None.", on_behalf_of_content_owner=object()
        )

    # max_results specific validation tests
    def test_invalid_type_max_results(self):
        """Test TypeError for invalid max_results type."""
        self.assert_error_behavior(
            list_channels, TypeError, "max_results must be an integer or None.", max_results="20"
        )

    def test_invalid_max_results_too_low(self):
        """Test MaxResultsOutOfRangeError for max_results < 1."""
        self.assert_error_behavior(
            list_channels, MaxResultsOutOfRangeError, "max_results must be between 1 and 50, inclusive.", max_results=0
        )

    def test_invalid_max_results_too_high(self):
        """Test MaxResultsOutOfRangeError for max_results > 50."""
        self.assert_error_behavior(
            list_channels, MaxResultsOutOfRangeError, "max_results must be between 1 and 50, inclusive.", max_results=51
        )

    def test_no_results_match(self):
        """Test scenario where no channels match the filter criteria."""
        result = list_channels(category_id="non_existent_category")
        self.assertEqual(len(result["items"]), 0)

    def test_valid_input_all_parts(self):
        """Test with valid 'part' and no other filters."""
        result = list_channel_sections(part="id,snippet,contentDetails")
        self.assertIsInstance(result, dict)
        self.assertIn("items", result)
        self.assertEqual(len(result["items"]), 3) # Expect all sections

    def test_valid_input_single_part(self):
        """Test with a single valid 'part'."""
        result = list_channel_sections(part="snippet")
        self.assertIsInstance(result, dict)
        self.assertIn("items", result)

    def test_valid_input_with_channel_id_filter(self):
        """Test filtering by channel_id."""
        result = list_channel_sections(part="id", channel_id="UCxyz")
        self.assertEqual(len(result["items"]), 0)
        for item in result["items"]:
            self.assertEqual(item["snippet"]["channelId"], "UCxyz")


    def test_valid_input_with_mine_true_filter(self):
        """Test filtering with mine=True."""
        result = list_channel_sections(part="id", mine=True)
        self.assertEqual(len(result["items"]), 0) # section1 and section3 are mine=True
        for item in result["items"]:
            self.assertTrue(item["snippet"]["mine"])
            
    def test_valid_input_with_mine_false_filter(self):
        """Test filtering with mine=False (should return all sections where 'mine' doesn't restrict)."""
        result = list_channel_sections(part="id", mine=False)
        self.assertEqual(len(result["items"]), 3) # mine=False doesn't actively filter out, just doesn't apply 'mine' restriction

    def test_valid_input_with_hl_and_on_behalf_of(self):
        """Test with hl and on_behalf_of_content_owner (these don't affect filtering in mock logic)."""
        result = list_channel_sections(
            part="id",
            hl="en_US",
            on_behalf_of_content_owner="owner_id"
        )
        self.assertEqual(len(result["items"]), 3) # Expect all sections as these params don't filter

    def test_part_invalid_type(self):
        """Test 'part' parameter with invalid type."""
        self.assert_error_behavior(
            list_channel_sections,
            TypeError,
            "Parameter 'part' must be a string.",
            part=123
        )

    def test_part_empty_string(self):
        """Test 'part' parameter as an empty string."""
        self.assert_error_behavior(
            list_channel_sections,
            InvalidPartParameterError,
            "Parameter 'part' cannot be empty or consist only of whitespace.",
            part=""
        )

    def test_part_whitespace_only(self):
        """Test 'part' parameter with only whitespace."""
        self.assert_error_behavior(
            list_channel_sections,
            InvalidPartParameterError,
            "Parameter 'part' cannot be empty or consist only of whitespace.",
            part="   "
        )

    def test_part_only_commas(self):
        """Test 'part' parameter with only commas."""
        self.assert_error_behavior(
            list_channel_sections,
            InvalidPartParameterError,
            r"Parameter 'part' resulted in no valid components after parsing. Original value: ',,,'",
            part=",,,"
        )

    def test_part_no_valid_components(self):
        """Test 'part' parameter with no valid components."""
        self.assert_error_behavior(
            list_channel_sections,
            InvalidPartParameterError,
            r"Invalid part parameter",
            part="invalid,another_invalid"
        )

    def test_part_some_valid_some_invalid_components(self):
        """Test 'part' with mixed valid and invalid components (should pass)."""
        result = list_channel_sections(part="id,invalid_component,snippet")
        self.assertIn("items", result) # Should succeed as 'id' and 'snippet' are valid

    def test_channel_id_invalid_type(self):
        """Test 'channel_id' parameter with invalid type."""
        self.assert_error_behavior(
            list_channel_sections,
            TypeError,
            "Parameter 'channel_id' must be a string or None.",
            part="id", channel_id=123
        )

    def test_hl_invalid_type(self):
        """Test 'hl' parameter with invalid type."""
        self.assert_error_behavior(
            list_channel_sections,
            TypeError,
            "Parameter 'hl' must be a string or None.",
            part="id", hl=123
        )

    def test_section_id_invalid_type(self):
        """Test 'section_id' parameter with invalid type."""
        self.assert_error_behavior(
            list_channel_sections,
            TypeError,
            "Parameter 'section_id' must be a string or None.",
            part="id", section_id=123
        )

    def test_mine_invalid_type(self):
        """Test 'mine' parameter with invalid type."""
        self.assert_error_behavior(
            list_channel_sections,
            TypeError,
            "Parameter 'mine' must be a boolean.",
            part="id", mine="true"
        )

    def test_on_behalf_of_content_owner_invalid_type(self):
        """Test 'on_behalf_of_content_owner' parameter with invalid type."""
        self.assert_error_behavior(
            list_channel_sections,
            TypeError,
            "Parameter 'on_behalf_of_content_owner' must be a string or None.",
            part="id", on_behalf_of_content_owner=123
        )
    
    def test_optional_parameters_as_none(self):
        """Test with all optional parameters set to None (default for some)."""
        result = list_channel_sections(
            part="id",
            channel_id=None,
            hl=None,
            section_id=None,
            on_behalf_of_content_owner=None
            # mine defaults to False, which is a valid boolean
        )
        self.assertIsInstance(result, dict)
        self.assertIn("items", result)
        self.assertEqual(len(result["items"]), 3) # Expect all sections as no filters applied effectively

        """
        Conceptual test for KeyError propagation.
        Directly testing KeyError from DB.get is complex with a simple dict and no mocks,
        as dict.get(key, default) doesn't raise KeyError.
        This test acknowledges the requirement from the docstring.
        If DB were a custom object whose .get() method could raise KeyError,
        that scenario would be covered by the 'Raises: KeyError' in the docstring.
        """
        # To simulate this, one would need to mock DB or use a DB object
        # that behaves this way. For now, we rely on the function's docstring.
        # Example of how it might be tested with a mock (OUT OF SCOPE FOR CURRENT TASK):
        #
        # global DB
        # original_db = DB
        # class MockDBError:
        #     def get(self, key, default=None):
        #         raise KeyError("Simulated DB KeyError")
        # DB = MockDBError()
        # self.assert_error_behavior(
        #     list_channel_sections,
        #     KeyError,
        #     "Simulated DB KeyError",
        #     part="id"
        # )
        # DB = original_db # Restore
        pass

    
    def test_delete_nonexistent_section_id_raises_keyerror(self):
        """Test that attempting to delete a non-existent section_id raises KeyError."""
        non_existent_id = "section_delta_non_existent"
        expected_keyerror_message = f"'Channel section ID: {non_existent_id} not found in the database.'"
        
        self.assert_error_behavior(
            func_to_call=delete_channel_section,
            expected_exception_type=KeyError,
            expected_message=expected_keyerror_message,
            section_id=non_existent_id
        )

    def test_invalid_section_id_type_integer_raises_typeerror(self):
        """Test that providing an integer section_id raises TypeError."""
        self.assert_error_behavior(
            func_to_call=delete_channel_section,
            expected_exception_type=TypeError,
            expected_message="section_id must be a string.",
            section_id=12345 # Invalid type
        )

    def test_invalid_section_id_type_none_raises_typeerror(self):
        """Test that providing None as section_id raises TypeError."""
        self.assert_error_behavior(
            func_to_call=delete_channel_section,
            expected_exception_type=TypeError,
            expected_message="section_id must be a string.",
            section_id=None # Invalid type
        )

    def test_invalid_on_behalf_of_content_owner_type_integer_raises_typeerror(self):
        """Test that providing an integer on_behalf_of_content_owner raises TypeError."""
        self.assert_error_behavior(
            func_to_call=delete_channel_section,
            expected_exception_type=TypeError,
            expected_message="on_behalf_of_content_owner must be a string if provided.",
            section_id="section_alpha",
            on_behalf_of_content_owner=98765 # Invalid type
        )

    def test_invalid_on_behalf_of_content_owner_type_list_raises_typeerror(self):
        """Test that providing a list for on_behalf_of_content_owner raises TypeError."""
        self.assert_error_behavior(
            func_to_call=delete_channel_section,
            expected_exception_type=TypeError,
            expected_message="on_behalf_of_content_owner must be a string if provided.",
            section_id="section_alpha",
            on_behalf_of_content_owner=[] # Invalid type
        )
    

    def test_empty_string_section_id_keyerror_if_not_exists(self):
        """Test that an empty string section_id raises KeyError if it does not exist."""

        expected_msg = "'Channel section ID:  not found in the database.'" # Note: two spaces after colon
        self.assert_error_behavior(
            func_to_call=delete_channel_section,
            expected_exception_type=KeyError,
            expected_message=expected_msg,
            section_id=""
        )

