# vim: set fileencoding=utf-8
import copy
import random
from typing import Any, Dict, List, Optional, Set, Tuple

from bemani.backend.jubeat.base import JubeatBase
from bemani.backend.jubeat.common import (
    JubeatDemodataGetHitchartHandler,
    JubeatDemodataGetNewsHandler,
    JubeatGamendRegisterHandler,
    JubeatGametopGetMeetingHandler,
    JubeatLobbyCheckHandler,
    JubeatLoggerReportHandler,
)
from bemani.backend.jubeat.clan import JubeatClan

from bemani.backend.base import Status
from bemani.common import Time, ValidatedDict, VersionConstants
from bemani.data import Data, Achievement, Score, Song, UserID
from bemani.protocol import Node


class JubeatFesto(
    JubeatDemodataGetHitchartHandler,
    JubeatDemodataGetNewsHandler,
    JubeatGamendRegisterHandler,
    JubeatGametopGetMeetingHandler,
    JubeatLobbyCheckHandler,
    JubeatLoggerReportHandler,
    JubeatBase,
):

    name = 'Jubeat Festo'
    version = VersionConstants.JUBEAT_FESTO

    JBOX_EMBLEM_NORMAL = 1
    JBOX_EMBLEM_PREMIUM = 2

    EVENT_STATUS_OPEN = 0x1
    EVENT_STATUS_COMPLETE = 0x2

    EVENTS = {
        5: {
            'enabled': False,
        },
        6: {
            'enabled': False,
        },
        15: {
            'enabled': True,
        },
        22: {
            'enabled': False,
        },
        23: {
            'enabled': False,
        },
        33: {
            'enabled': False,
        },
        101: {
            'enabled': False,
        }
    }
    JBOX_EMBLEM_NORMAL = 1
    JBOX_EMBLEM_PREMIUM = 2

    FIVE_PLAYS_UNLOCK_EVENT_SONG_IDS = set(range(80000301, 80000348))

    COURSE_STATUS_SEEN = 0x01
    COURSE_STATUS_PLAYED = 0x02
    COURSE_STATUS_CLEARED = 0x04

    COURSE_TYPE_PERMANENT = 1
    COURSE_TYPE_TIME_BASED = 2

    COURSE_CLEAR_SCORE = 1
    COURSE_CLEAR_COMBINED_SCORE = 2
    COURSE_CLEAR_HAZARD = 3

    COURSE_HAZARD_EXC1 = 1
    COURSE_HAZARD_EXC2 = 2
    COURSE_HAZARD_EXC3 = 3
    COURSE_HAZARD_FC1 = 4
    COURSE_HAZARD_FC2 = 5
    COURSE_HAZARD_FC3 = 6

    def previous_version(self) -> Optional[JubeatBase]:
        return JubeatClan(self.data, self.config, self.model)

    @classmethod
    def run_scheduled_work(cls, data: Data, config: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Insert daily FC challenges into the DB.
        """
        events = []
        if data.local.network.should_schedule(cls.game, cls.version, 'fc_challenge', 'daily'):
            # Generate a new list of two FC challenge songs. Skip a particular song range since these are all a single song ID.
            # Jubeat Clan has an unlock event where you have to play different charts for the same song, and the charts are
            # loaded in based on the cabinet's prefecture. So, no matter where you are, you will only see one song within this
            # range, but it will be a different ID depending on the prefecture set in settings. This means its not safe to send
            # these song IDs, so we explicitly exclude them.
            start_time, end_time = data.local.network.get_schedule_duration('daily')
            all_songs = set(song.id for song in data.local.music.get_all_songs(cls.game, cls.version) if song.id not in cls.FIVE_PLAYS_UNLOCK_EVENT_SONG_IDS)
            daily_songs = random.sample(all_songs, 2)
            data.local.game.put_time_sensitive_settings(
                cls.game,
                cls.version,
                'fc_challenge',
                {
                    'start_time': start_time,
                    'end_time': end_time,
                    'today': daily_songs[0],
                    'whim': daily_songs[1],
                },
            )
            events.append((
                'jubeat_fc_challenge_charts',
                {
                    'version': cls.version,
                    'today': daily_songs[0],
                    'whim': daily_songs[1],
                },
            ))

            # Mark that we did some actual work here.
            data.local.network.mark_scheduled(cls.game, cls.version, 'fc_challenge', 'daily')
        return events

    def __get_course_list(self) -> List[Dict[str, Any]]:
        # Full course list found at http://bemaniwiki.com/index.php?jubeat%20festo/TUNE%20RUN
        return [
            # ASARI CUP
            {
                'id': 1,
                'name': 'はじめてのビーチ',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_SCORE,
                'difficulty': 1,
                'score': 700000,
                'music': [
                    [(60000080, 0), (90000025, 0), (90000040, 0)],
                    [(60000086, 0), (70000047, 0)],
                    [(90000027, 0)],
                ],
            },
            {
                'id': 2,
                'name': '【初段】超幸せハイテンション',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_SCORE,
                'difficulty': 1,
                'score': 700000,
                'music': [
                    [(60000100, 0), (90000030, 0), (90000079, 0)],
                    [(70000125, 0), (90000050, 0)],
                    [(70000106, 0)],
                ],
            },
            {
                'id': 3,
                'name': 'アニメランニング',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_SCORE,
                'difficulty': 2,
                'score': 750000,
                'music': [
                    [(90000031, 0), (90000037, 0), (90000082, 0)],
                    [(80000120, 0)],
                    [(80000125, 0)],
                ],
            },
            {
                'id': 4,
                'name': 'パブリックリゾート',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_SCORE,
                'difficulty': 2,
                'score': 750000,
                'music': [
                    [(90000040, 0), (50000296, 0), (90000044, 0)],
                    [(90000033, 0), (90000039, 0)],
                    [(80000091, 0)],
                ],
            },
            {
                'id': 5,
                'name': '【二段】その笑顔は甘く蕩ける',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_SCORE,
                'difficulty': 3,
                'score': 800000,
                'music': [
                    [(50000268, 0), (70000039, 0), (90000051, 0)],
                    [(70000091, 0), (70000042, 0)],
                    [(60000053, 0)],
                ],
            },
            # KISAGO CUP
            {
                'id': 11,
                'name': '電脳享受空間',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_SCORE,
                'difficulty': 4,
                'score': 800000,
                'music': [
                    [(70000046, 1), (70000160, 1), (80000126, 1)],
                    [(80000031, 1), (80000097, 1)],
                    [(90000049, 1)],
                ],
            },
            {
                'id': 12,
                'name': '孤高の少女は破滅を願う',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_SCORE,
                'difficulty': 4,
                'score': 850000,
                'music': [
                    [(50000202, 0), (70000117, 0), (70000134, 0)],
                    [(50000212, 0), (80000124, 1)],
                    [(90001008, 1)],
                ],
            },
            {
                'id': 13,
                'name': 'スタミナアップ！',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_COMBINED_SCORE,
                'difficulty': 5,
                'score': 2600000,
                'music': [
                    [(50000242, 0), (90000037, 1)],
                    [(50000260, 1), (50000261, 1)],
                    [(90000081, 1)],
                ],
            },
            {
                'id': 14,
                'name': '【三段】この花を貴方へ',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_SCORE,
                'difficulty': 4,
                'score': 850000,
                'music': [
                    [(90000034, 1), (90000037, 1), (90000042, 1)],
                    [(80000120, 1), (80001010, 1)],
                    [(40000051, 1)],
                ],
            },
            {
                'id': 15,
                'name': '【四段】嗚呼、大繁盛！',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_COMBINED_SCORE,
                'difficulty': 6,
                'score': 2600000,
                'music': [
                    [(50000085, 2), (50000237, 2), (80000080, 2)],
                    [(50000172, 2), (50000235, 2)],
                    [(70000065, 2)],
                ],
            },
            # MURU CUP
            {
                'id': 21,
                'name': '黒船来航',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_SCORE,
                'difficulty': 7,
                'score': 850000,
                'music': [
                    [(50000086, 2), (60000066, 2), (80000040, 1)],
                    [(50000096, 2), (80000048, 2)],
                    [(50000091, 2)],
                ],
            },
            {
                'id': 22,
                'name': '【五段】濁流を乗り越えて',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_COMBINED_SCORE,
                'difficulty': 7,
                'score': 2650000,
                'music': [
                    [(50000343, 2), (60000060, 1), (60000071, 2)],
                    [(60000027, 2), (80000048, 2)],
                    [(20000038, 2)],
                ],
            },
            {
                'id': 23,
                'name': 'のんびり。ゆったり。ほがらかに。',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_SCORE,
                'difficulty': 8,
                'score': 950000,
                'music': [
                    [(40000154, 2), (80000124, 1), (80000126, 2)],
                    [(60000048, 2), (90000026, 2)],
                    [(90000050, 2)],
                ],
            },
            {
                'id': 24,
                'name': '海・KOI・スィニョーレ！！',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_COMBINED_SCORE,
                'difficulty': 8,
                'score': 2650000,
                'music': [
                    [(50000201, 2)],
                    [(50000339, 2)],
                    [(50000038, 2)],
                ],
            },
            {
                'id': 25,
                'name': '【六段】電柱を見ると思出す',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_COMBINED_SCORE,
                'difficulty': 9,
                'score': 2750000,
                'music': [
                    [(50000288, 2), (80000046, 2), (80001008, 2)],
                    [(50000207, 2), (70000117, 2)],
                    [(30000048, 2)],
                ],
            },
            # SAZAE CUP
            {
                'id': 31,
                'name': '超フェスタ！',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_SCORE,
                'difficulty': 10,
                'score': 930000,
                'music': [
                    [(70000076, 2), (70000077, 2)],
                    [(20000038, 2), (40000160, 2)],
                    [(70000145, 2)],
                ],
            },
            {
                'id': 32,
                'name': '【七段】操り人形はほくそ笑む',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_COMBINED_SCORE,
                'difficulty': 10,
                'score': 2800000,
                'music': [
                    [(70000006, 2), (70000171, 2), (80000003, 2)],
                    [(50000078, 2), (50000324, 2)],
                    [(80000118, 2)],
                ],
            },
            {
                'id': 33,
                'name': '絶体絶命スリーチャレンジ！',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_HAZARD,
                'hazard_type': self.COURSE_HAZARD_FC3,
                'difficulty': 11,
                'score': 2800000,
                'music': [
                    [(50000238, 2), (70000003, 2), (90000051, 1)],
                    [(50000027, 2), (50000387, 2)],
                    [(80000056, 2)],
                ],
            },
            {
                'id': 34,
                'name': '天国の舞踏会',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_COMBINED_SCORE,
                'difficulty': 11,
                'score': 2800000,
                'music': [
                    [(60000065, 1)],
                    [(80001007, 2)],
                    [(90001007, 2)],
                ],
            },
            {
                'id': 35,
                'name': '【八段】山の賽子',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_COMBINED_SCORE,
                'difficulty': 12,
                'score': 2820000,
                'music': [
                    [(50000200, 2), (50000291, 2), (60000003, 2)],
                    [(50000129, 2), (80000021, 2)],
                    [(80000087, 2)],
                ],
            },
            # HOTATE CUP
            {
                'id': 41,
                'name': 'The 8th KAC 個人部門',
                'course_type': self.COURSE_TYPE_TIME_BASED,
                'end_time': Time.end_of_this_week() + Time.SECONDS_IN_WEEK,
                'clear_type': self.COURSE_CLEAR_SCORE,
                'hard': True,
                'difficulty': 14,
                'score': 700000,
                'music': [
                    [(90000052, 2)],
                    [(90000013, 2)],
                    [(70000167, 2)],
                ],
            },
            {
                'id': 42,
                'name': 'The 8th KAC 団体部門',
                'course_type': self.COURSE_TYPE_TIME_BASED,
                'end_time': Time.end_of_this_week() + Time.SECONDS_IN_WEEK,
                'clear_type': self.COURSE_CLEAR_SCORE,
                'hard': True,
                'difficulty': 14,
                'score': 700000,
                'music': [
                    [(90000009, 2)],
                    [(80000133, 2)],
                    [(80000101, 2)],
                ],
            },
            {
                'id': 43,
                'name': 'BEMANI MASTER KOREA 2019',
                'course_type': self.COURSE_TYPE_TIME_BASED,
                'end_time': Time.end_of_this_week() + Time.SECONDS_IN_WEEK,
                'clear_type': self.COURSE_CLEAR_SCORE,
                'hard': True,
                'difficulty': 14,
                'score': 700000,
                'music': [
                    [(90000003, 2)],
                    [(80000090, 2)],
                    [(90000009, 2)],
                ],
            },
            {
                'id': 44,
                'name': '初めてのHARD MODE再び',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_COMBINED_SCORE,
                'hard': True,
                'difficulty': 13,
                'score': 2750000,
                'music': [
                    [(50000096, 2), (50000263, 2), (80000119, 2)],
                    [(60000021, 2), (60000075, 2)],
                    [(60000039, 2)],
                ],
            },
            {
                'id': 45,
                'name': '【九段】2人からの挑戦状',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_COMBINED_SCORE,
                'difficulty': 13,
                'score': 2830000,
                'music': [
                    [(50000023, 2), (80000025, 2), (80000106, 2)],
                    [(50000124, 2), (80000082, 2)],
                    [(60000115, 2)],
                ],
            },
            {
                'id': 46,
                'name': '天空の庭　太陽の園',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_SCORE,
                'difficulty': 13,
                'score': 965000,
                'music': [
                    [(40000153, 2)],
                    [(80000007, 2)],
                    [(70000173, 2)],
                ],
            },
            {
                'id': 47,
                'name': '緊急！迅速！大混乱！',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_COMBINED_SCORE,
                'difficulty': 14,
                'score': 2900000,
                'music': [
                    [(20000040, 2), (50000244, 2), (70000145, 2)],
                    [(40000046, 2), (50000158, 2)],
                    [(40000057, 2)],
                ],
            },
            {
                'id': 48,
                'name': '【十段】時の超越者',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_COMBINED_SCORE,
                'hard': True,
                'difficulty': 14,
                'score': 2820000,
                'music': [
                    [(20000051, 2), (50000249, 2), (70000108, 2)],
                    [(40000046, 2), (50000180, 2)],
                    [(50000134, 2)],
                ],
            },
            # OSHAKO CUP
            {
                'id': 51,
                'name': '【皆伝】甘味なのに甘くない',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_COMBINED_SCORE,
                'hard': True,
                'difficulty': 15,
                'score': 2850000,
                'music': [
                    [(90000010, 2)],
                    [(80000101, 2)],
                    [(50000102, 2)],
                ],
            },
            {
                'id': 52,
                'name': '【伝導】真の青が魅せた空',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_SCORE,
                'hard': True,
                'difficulty': 15,
                'score': 970000,
                'music': [
                    [(50000332, 2)],
                    [(70000098, 2)],
                    [(90001005, 2)],
                ],
            },
            {
                'id': 53,
                'name': '豪華絢爛高揚絶頂',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_COMBINED_SCORE,
                'hard': True,
                'difficulty': 16,
                'score': 2960000,
                'music': [
                    [(10000065, 2)],
                    [(50000323, 2)],
                    [(50000208, 2)],
                ],
            },
            {
                'id': 54,
                'name': '絢爛豪華激情無常',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_COMBINED_SCORE,
                'hard': True,
                'difficulty': 16,
                'score': 2960000,
                'music': [
                    [(60000010, 2)],
                    [(70000110, 2)],
                    [(90000047, 2)],
                ],
            },
            {
                'id': 55,
                'name': '【指神】王の降臨',
                'course_type': self.COURSE_TYPE_PERMANENT,
                'clear_type': self.COURSE_CLEAR_COMBINED_SCORE,
                'hard': True,
                'difficulty': 16,
                'score': 2980000,
                'music': [
                    [(70000094, 2)],
                    [(80000088, 2)],
                    [(70000110, 2)],
                ],
            },
        ]

    def __get_global_info(self) -> Node:
        info = Node.void('info')

        # Event info.
        event_info = Node.void('event_info')
        info.add_child(event_info)
        for event in self.EVENTS:
            evt = Node.void('event')
            event_info.add_child(evt)
            evt.set_attribute('type', str(event))
            evt.add_child(Node.u8('state', self.EVENT_STATUS_OPEN if self.EVENTS[event]['enabled'] else 0))

        genre_def_music = Node.void('genre_def_music')
        info.add_child(genre_def_music)

        info.add_child(Node.s32_array(
            'black_jacket_list',
            [
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
            ],
        ))

        # Some sort of music DB whitelist
        info.add_child(Node.s32_array(
            'white_music_list',
            [
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
            ],
        ))

        info.add_child(Node.s32_array(
            'white_marker_list',
            [
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
            ],
        ))

        info.add_child(Node.s32_array(
            'white_theme_list',
            [
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
            ],
        ))

        info.add_child(Node.s32_array(
            'open_music_list',
            [
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
            ],
        ))

        info.add_child(Node.s32_array(
            'shareable_music_list',
            [
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
                -1, -1, -1, -1,
            ],
        ))

        info.add_child(Node.s32_array(
            'hot_music_list',
            [
                0, 0, 0, 0, 
                0, 0, 0, 0, 
                0, 0, 0, 0, 
                0, 0, 0, 0, 
                0, 0, 0, 0, 
                0, 0, 0, 0, 
                0, 0, 0, 0, 
                0, 0, 0, 0, 
                0, 0, 0, 0, 
                0, -4194304, -2080769, -5, 
                -17, -35651587, 234571775, 939654912, 
                14, 0, 0, 0, 
                0, 0, 0, 0, 
                0, 0, 0, 0, 
                0, 0, 0, 0, 
                0, 0, 0, 0, 
            ]
        ))

        jbox = Node.void('jbox')
        info.add_child(jbox)
        jbox.add_child(Node.s32('point', 0))
        emblem = Node.void('emblem')
        jbox.add_child(emblem)
        normal = Node.void('normal')
        emblem.add_child(normal)
        premium = Node.void('premium')
        emblem.add_child(premium)
        normal.add_child(Node.s16('index', 2))
        premium.add_child(Node.s16('index', 1))

        born = Node.void('born')
        info.add_child(born)
        born.add_child(Node.s8('status', 0))
        born.add_child(Node.s16('year', 0))

        # Collection list values should look like:
        #     <rating>
        #         <id __type="s32">songid</id>
        #         <stime __type="str">start time?</stime>
        #         <etime __type="str">end time?</etime>
        #     </node>
        collection = Node.void('collection')
        info.add_child(collection)
        collection.add_child(Node.void('rating_s'))

        konami_logo_50th = Node.void('konami_logo_50th')
        info.add_child(konami_logo_50th)
        konami_logo_50th.add_child(Node.bool('is_available', True))

        expert_option = Node.void('expert_option')
        info.add_child(expert_option)
        expert_option.add_child(Node.bool('is_available', True))

        all_music_matching = Node.void('all_music_matching')
        info.add_child(all_music_matching)
        all_music_matching.add_child(Node.bool('is_available', True))
        department = Node.void('department')
        all_music_matching.add_child(department)
        department.add_child(Node.void('pack_list'))

        question_list = Node.void('question_list')
        info.add_child(question_list)

        # Set up TUNE RUN course requirements
        clan_course_list = Node.void('course_list')
        #info.add_child(clan_course_list)

        valid_courses: Set[int] = set()
        for course in self.__get_course_list():
            if course['id'] < 1:
                raise Exception(f"Invalid course ID {course['id']} found in course list!")
            if course['id'] in valid_courses:
                raise Exception(f"Duplicate ID {course['id']} found in course list!")
            if course['clear_type'] == self.COURSE_CLEAR_HAZARD and 'hazard_type' not in course:
                raise Exception(f"Need 'hazard_type' set in course {course['id']}!")
            if course['course_type'] == self.COURSE_TYPE_TIME_BASED and 'end_time' not in course:
                raise Exception(f"Need 'end_time' set in course {course['id']}!")
            if course['clear_type'] in [self.COURSE_CLEAR_SCORE, self.COURSE_CLEAR_COMBINED_SCORE] and 'score' not in course:
                raise Exception(f"Need 'score' set in course {course['id']}!")
            if course['clear_type'] == self.COURSE_CLEAR_SCORE and course['score'] > 1000000:
                raise Exception(f"Invalid per-coure score in course {course['id']}!")
            if course['clear_type'] == self.COURSE_CLEAR_COMBINED_SCORE and course['score'] <= 1000000:
                raise Exception(f"Invalid combined score in course {course['id']}!")
            valid_courses.add(course['id'])

            # Basics
            clan_course = Node.void('course')
            clan_course_list.add_child(clan_course)
            clan_course.set_attribute('release_code', '2018112700')
            clan_course.set_attribute('version_id', '0')
            clan_course.set_attribute('id', str(course['id']))
            clan_course.set_attribute('course_type', str(course['course_type']))
            clan_course.add_child(Node.s32('difficulty', course['difficulty']))
            clan_course.add_child(Node.u64('etime', (course['end_time'] if 'end_time' in course else 0) * 1000))
            clan_course.add_child(Node.string('name', course['name']))

            # List of included songs
            tune_list = Node.void('tune_list')
            clan_course.add_child(tune_list)
            for order, charts in enumerate(course['music']):
                tune = Node.void('tune')
                tune_list.add_child(tune)
                tune.set_attribute('no', str(order + 1))

                seq_list = Node.void('seq_list')
                tune.add_child(seq_list)

                for songid, chart in charts:
                    seq = Node.void('seq')
                    seq_list.add_child(seq)
                    seq.add_child(Node.s32('music_id', songid))
                    seq.add_child(Node.s32('difficulty', chart))
                    seq.add_child(Node.bool('is_secret', False))

            # Clear criteria
            clear = Node.void('clear')
            clan_course.add_child(clear)
            ex_option = Node.void('ex_option')
            clear.add_child(ex_option)
            ex_option.add_child(Node.bool('is_hard', course['hard'] if 'hard' in course else False))
            ex_option.add_child(Node.s32('hazard_type', course['hazard_type'] if 'hazard_type' in course else 0))
            clear.set_attribute('type', str(course['clear_type']))
            clear.add_child(Node.s32('score', course['score'] if 'score' in course else 0))

            reward_list = Node.void('reward_list')
            clear.add_child(reward_list)
        # add stuff for newer festo to boot

        info.add_child(Node.void('share_music'))
        info.add_child(Node.void('weekly_music'))
        info.add_child(Node.s32_array(
            'add_default_music_list',
            [
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
                0, 0, 0, 0,
            ],
        ))
        info.add_child(Node.void('department'))
        info.add_child(Node.void('team_battle'))
        info.add_child(Node.void('emo_list'))
        info.add_child(Node.void('tip_list'))
        return info

    def handle_shopinfo_regist_request(self, request: Node) -> Node:
        # Update the name of this cab for admin purposes
        self.update_machine_name(request.child_value('shop/name'))

        shopinfo = Node.void('shopinfo')

        data = Node.void('data')
        shopinfo.add_child(data)
        data.add_child(Node.u32('cabid', 1))
        data.add_child(Node.string('locationid', 'nowhere'))
        data.add_child(Node.u8('tax_phase', 1))

        facility = Node.void('facility')
        data.add_child(facility)
        facility.add_child(Node.u32('exist', 1))
        data.add_child(self.__get_global_info())

        return shopinfo

    def handle_demodata_get_info_request(self, request: Node) -> Node:
        root = Node.void('demodata')
        data = Node.void('data')
        root.add_child(data)
        officialnews = Node.void('officialnews')
        officialnews.set_attribute('count', '0')
        data.add_child(officialnews)

        return root

    def handle_demodata_get_jbox_list_request(self, request: Node) -> Node:
        root = Node.void('demodata')
        return root

    def handle_jbox_get_agreement_request(self, request: Node) -> Node:
        root = Node.void('jbox')
        root.add_child(Node.bool('is_agreement', True))
        return root

    def handle_jbox_get_list_request(self, request: Node) -> Node:
        root = Node.void('jbox')
        root.add_child(Node.void('selection_list'))
        return root

    def handle_recommend_get_recommend_request(self, request: Node) -> Node:
        recommend = Node.void('recommend')
        data = Node.void('data')
        recommend.add_child(data)

        player = Node.void('player')
        data.add_child(player)
        music_list = Node.void('music_list')
        player.add_child(music_list)

        recommended_songs: List[Song] = []
        for i, song in enumerate(recommended_songs):
            music = Node.void('music')
            music_list.add_child(music)
            music.set_attribute('order', str(i))
            music.add_child(Node.s32('music_id', song.id))
            music.add_child(Node.s8('seq', song.chart))

        return recommend

    def handle_gametop_get_info_request(self, request: Node) -> Node:
        root = Node.void('gametop')
        data = Node.void('data')
        root.add_child(data)
        data.add_child(self.__get_global_info())

        return root

    def handle_gametop_regist_request(self, request: Node) -> Node:
        data = request.child('data')
        player = data.child('player')
        refid = player.child_value('refid')
        name = player.child_value('name')
        root = self.new_profile_by_refid(refid, name)
        return root

    def handle_gametop_get_pdata_request(self, request: Node) -> Node:
        data = request.child('data')
        player = data.child('player')
        refid = player.child_value('refid')
        root = self.get_profile_by_refid(refid)
        if root is None:
            root = Node.void('gametop')
            root.set_attribute('status', str(Status.NO_PROFILE))
        return root

    def handle_gametop_get_mdata_request(self, request: Node) -> Node:
        data = request.child('data')
        player = data.child('player')
        extid = player.child_value('jid')
        root = self.get_scores_by_extid(extid)
        if root is None:
            root = Node.void('gametop')
            root.set_attribute('status', str(Status.NO_PROFILE))
        return root

    def handle_gameend_final_request(self, request: Node) -> Node:
        data = request.child('data')
        player = data.child('player')

        if player is not None:
            refid = player.child_value('refid')
        else:
            refid = None

        if refid is not None:
            userid = self.data.remote.user.from_refid(self.game, self.version, refid)
        else:
            userid = None

        if userid is not None:
            profile = self.get_profile(userid)

            # Grab unlock progress
            item = player.child('item')
            if item is not None:
                profile.replace_int_array('emblem_list', 96, item.child_value('emblem_list'))

            # jbox stuff
            jbox = player.child('jbox')
            jboxdict = profile.get_dict('jbox')
            if jbox is not None:
                jboxdict.replace_int('point', jbox.child_value('point'))
                emblemtype = jbox.child_value('emblem/type')
                index = jbox.child_value('emblem/index')
                if emblemtype == self.JBOX_EMBLEM_NORMAL:
                    jboxdict.replace_int('normal_index', index)
                elif emblemtype == self.JBOX_EMBLEM_PREMIUM:
                    jboxdict.replace_int('premium_index', index)
            profile.replace_dict('jbox', jboxdict)

            # Born stuff
            born = player.child('born')
            if born is not None:
                profile.replace_int('born_status', born.child_value('status'))
                profile.replace_int('born_year', born.child_value('year'))
        else:
            profile = None

        if userid is not None and profile is not None:
            self.put_profile(userid, profile)

        return Node.void('gameend')

    def format_scores(self, userid: UserID, profile: ValidatedDict, scores: List[Score]) -> Node:
        scores = self.data.remote.music.get_scores(self.game, self.music_version, userid)

        root = Node.void('gametop')
        datanode = Node.void('data')
        root.add_child(datanode)
        player = Node.void('player')
        datanode.add_child(player)
        player.add_child(Node.s32('jid', profile.get_int('extid')))
        playdata = Node.void('mdata_list')
        player.add_child(playdata)

        music = ValidatedDict()
        for score in scores:
            # Normal Mode
            if score.chart < 3:
                data = music.get_dict(str(score.id))
                play_cnt = data.get_int_array('play_cnt', 3)
                clear_cnt = data.get_int_array('clear_cnt', 3)
                clear_flags = data.get_int_array('clear_flags', 3)
                fc_cnt = data.get_int_array('fc_cnt', 3)
                ex_cnt = data.get_int_array('ex_cnt', 3)
                points = data.get_int_array('points', 3)
                music_rate = data.get_int_array('music_rate', 3)

                # Replace data for this chart type
                play_cnt[score.chart] = score.plays
                clear_cnt[score.chart] = score.data.get_int('clear_count')
                fc_cnt[score.chart] = score.data.get_int('full_combo_count')
                ex_cnt[score.chart] = score.data.get_int('excellent_count')
                points[score.chart] = score.points
                music_rate[score.chart] = score.data.get_int('music_rate')

                # Format the clear flags
                clear_flags[score.chart] = self.GAME_FLAG_BIT_PLAYED
                if score.data.get_int('clear_count') > 0:
                    clear_flags[score.chart] |= self.GAME_FLAG_BIT_CLEARED
                if score.data.get_int('full_combo_count') > 0:
                    clear_flags[score.chart] |= self.GAME_FLAG_BIT_FULL_COMBO
                if score.data.get_int('excellent_count') > 0:
                    clear_flags[score.chart] |= self.GAME_FLAG_BIT_EXCELLENT

                # Save chart data back
                data.replace_int_array('play_cnt', 3, play_cnt)
                data.replace_int_array('clear_cnt', 3, clear_cnt)
                data.replace_int_array('clear_flags', 3, clear_flags)
                data.replace_int_array('fc_cnt', 3, fc_cnt)
                data.replace_int_array('ex_cnt', 3, ex_cnt)
                data.replace_int_array('points', 3, points)
                data.replace_int_array('music_rate', 3, music_rate)
                # Update the ghost (untyped)
                ghost = data.get('ghost', [None, None, None])
                ghost[score.chart] = score.data.get('ghost')
                data['ghost'] = ghost
            # Hard Mode
            else:
                chart = score.chart - 3
                data = music.get_dict(str(score.id))
                play_cnt = data.get_int_array('hard_play_cnt', 3)
                clear_cnt = data.get_int_array('hard_clear_cnt', 3)
                clear_flags = data.get_int_array('hard_clear_flags', 3)
                fc_cnt = data.get_int_array('hard_fc_cnt', 3)
                ex_cnt = data.get_int_array('hard_ex_cnt', 3)
                points = data.get_int_array('hard_points', 3)
                music_rate = data.get_int_array('hard_music_rate', 3)

                # Replace data for this chart type
                play_cnt[chart] = score.plays
                clear_cnt[chart] = score.data.get_int('clear_count')
                fc_cnt[chart] = score.data.get_int('full_combo_count')
                ex_cnt[chart] = score.data.get_int('excellent_count')
                points[chart] = score.points
                music_rate[chart] = score.data.get_int('music_rate')

                # Format the clear flags
                clear_flags[chart] = self.GAME_FLAG_BIT_PLAYED
                if score.data.get_int('clear_count') > 0:
                    clear_flags[chart] |= self.GAME_FLAG_BIT_CLEARED
                if score.data.get_int('full_combo_count') > 0:
                    clear_flags[chart] |= self.GAME_FLAG_BIT_FULL_COMBO
                if score.data.get_int('excellent_count') > 0:
                    clear_flags[chart] |= self.GAME_FLAG_BIT_EXCELLENT

                # Save chart data back
                data.replace_int_array('hard_play_cnt', 3, play_cnt)
                data.replace_int_array('hard_clear_cnt', 3, clear_cnt)
                data.replace_int_array('hard_clear_flags', 3, clear_flags)
                data.replace_int_array('hard_fc_cnt', 3, fc_cnt)
                data.replace_int_array('hard_ex_cnt', 3, ex_cnt)
                data.replace_int_array('hard_points', 3, points)
                data.replace_int_array('hard_music_rate', 3, music_rate)
                # Update the ghost (untyped)
                ghost = data.get('hard_ghost', [None, None, None])
                ghost[chart] = score.data.get('ghost')
                data['hard_ghost'] = ghost
            # Save it back
            if score.id in self.FIVE_PLAYS_UNLOCK_EVENT_SONG_IDS:
                # Mirror it to every version so the score shows up regardless of
                # prefecture setting.
                for prefecture_id in self.FIVE_PLAYS_UNLOCK_EVENT_SONG_IDS:
                    music.replace_dict(str(prefecture_id), data)
            else:
                # Regular copy.
                music.replace_dict(str(score.id), data)

        for scoreid in music:
            scoredata = music.get_dict(scoreid)
            musicdata = Node.void('musicdata')
            playdata.add_child(musicdata)
            musicdata.set_attribute('music_id', scoreid)

            normal = Node.void('normal')
            musicdata.add_child(normal)
            normal.add_child(Node.s32_array('play_cnt', scoredata.get_int_array('play_cnt', 3)))
            normal.add_child(Node.s32_array('clear_cnt', scoredata.get_int_array('clear_cnt', 3)))
            normal.add_child(Node.s32_array('fc_cnt', scoredata.get_int_array('fc_cnt', 3)))
            normal.add_child(Node.s32_array('ex_cnt', scoredata.get_int_array('ex_cnt', 3)))
            normal.add_child(Node.s32_array('score', scoredata.get_int_array('points', 3)))
            normal.add_child(Node.s8_array('clear', scoredata.get_int_array('clear_flags', 3)))
            normal.add_child(Node.s32_array('music_rate', scoredata.get_int_array('music_rate', 3)))

            for i, ghost in enumerate(scoredata.get('ghost', [None, None, None])):
                if ghost is None:
                    continue

                bar = Node.u8_array('bar', ghost)
                normal.add_child(bar)
                bar.set_attribute('seq', str(i))

            hard = Node.void('hard')
            musicdata.add_child(hard)
            hard.add_child(Node.s32_array('play_cnt', scoredata.get_int_array('hard_play_cnt', 3)))
            hard.add_child(Node.s32_array('clear_cnt', scoredata.get_int_array('hard_clear_cnt', 3)))
            hard.add_child(Node.s32_array('fc_cnt', scoredata.get_int_array('hard_fc_cnt', 3)))
            hard.add_child(Node.s32_array('ex_cnt', scoredata.get_int_array('hard_ex_cnt', 3)))
            hard.add_child(Node.s32_array('score', scoredata.get_int_array('hard_points', 3)))
            hard.add_child(Node.s8_array('clear', scoredata.get_int_array('hard_clear_flags', 3)))
            hard.add_child(Node.s32_array('music_rate', scoredata.get_int_array('hard_music_rate', 3)))

            for i, ghost in enumerate(scoredata.get('hard_ghost', [None, None, None])):
                if ghost is None:
                    continue

                bar = Node.u8_array('bar', ghost)
                hard.add_child(bar)
                bar.set_attribute('seq', str(i))

        return root

    def format_profile(self, userid: UserID, profile: ValidatedDict) -> Node:
        root = Node.void('gametop')
        data = Node.void('data')
        root.add_child(data)

        # Jubeat Clan appears to allow full event overrides per-player
        data.add_child(self.__get_global_info())

        player = Node.void('player')
        data.add_child(player)

        # Basic profile info
        player.add_child(Node.string('name', profile.get_str('name', 'なし')))
        player.add_child(Node.s32('jid', profile.get_int('extid')))

        # Miscelaneous crap
        player.add_child(Node.s32('session_id', 1))
        player.add_child(Node.u64('event_flag', profile.get_int('event_flag')))

        # Player info and statistics
        info = Node.void('info')
        player.add_child(info)
        info.add_child(Node.s32('tune_cnt', profile.get_int('tune_cnt')))
        info.add_child(Node.s32('save_cnt', profile.get_int('save_cnt')))
        info.add_child(Node.s32('saved_cnt', profile.get_int('saved_cnt')))
        info.add_child(Node.s32('fc_cnt', profile.get_int('fc_cnt')))
        info.add_child(Node.s32('ex_cnt', profile.get_int('ex_cnt')))
        info.add_child(Node.s32('clear_cnt', profile.get_int('clear_cnt')))
        info.add_child(Node.s32('match_cnt', profile.get_int('match_cnt')))
        info.add_child(Node.s32('beat_cnt', profile.get_int('beat_cnt')))
        info.add_child(Node.s32('mynews_cnt', profile.get_int('mynews_cnt')))
        info.add_child(Node.s32('bonus_tune_points', profile.get_int('bonus_tune_points')))
        info.add_child(Node.bool('is_bonus_tune_played', profile.get_bool('is_bonus_tune_played')))

        # Looks to be set to true when there's an old profile, stops tutorial from
        # happening on first load.
        # Should only be true on the first load, stuff breaks otherwise
        info.add_child(Node.bool('inherit', False))

        # Not saved, but loaded
        info.add_child(Node.s32('mtg_entry_cnt', 123))
        info.add_child(Node.s32('mtg_hold_cnt', 456))
        info.add_child(Node.u8('mtg_result', 10))

        # Last played data, for showing cursor and such
        lastdict = profile.get_dict('last')
        last = Node.void('last')
        player.add_child(last)
        last.add_child(Node.s64('play_time', lastdict.get_int('play_time')))
        last.add_child(Node.string('shopname', lastdict.get_str('shopname')))
        last.add_child(Node.string('areaname', lastdict.get_str('areaname')))
        last.add_child(Node.s32('music_id', lastdict.get_int('music_id')))
        last.add_child(Node.s8('seq_id', lastdict.get_int('seq_id')))
        last.add_child(Node.string('seq_edit_id', '12345678'))
        last.add_child(Node.s8('sort', lastdict.get_int('sort')))
        last.add_child(Node.s8('category', lastdict.get_int('category')))
        last.add_child(Node.s8('expert_option', lastdict.get_int('expert_option')))

        settings = Node.void('settings')
        last.add_child(settings)
        settings.add_child(Node.s8('marker', lastdict.get_int('marker')))
        settings.add_child(Node.s8('theme', lastdict.get_int('theme')))
        settings.add_child(Node.s16('title', lastdict.get_int('title')))
        settings.add_child(Node.s16('parts', lastdict.get_int('parts')))
        settings.add_child(Node.s8('rank_sort', lastdict.get_int('rank_sort')))
        settings.add_child(Node.s8('combo_disp', lastdict.get_int('combo_disp')))
        settings.add_child(Node.s16_array('emblem', lastdict.get_int_array('emblem', 5)))
        settings.add_child(Node.s8('matching', lastdict.get_int('matching')))
        settings.add_child(Node.s8('hard', lastdict.get_int('hard')))
        settings.add_child(Node.s8('hazard', lastdict.get_int('hazard')))

        # Secret unlocks
        item = Node.void('item')
        player.add_child(item)
        item.add_child(Node.s32_array('music_list', profile.get_int_array('music_list', 64, [-1] * 64)))
        item.add_child(Node.s32_array('secret_list', profile.get_int_array('secret_list', 64, [-1] * 64)))
        item.add_child(Node.s32_array('theme_list', profile.get_int_array('theme_list', 16, [-1] * 16)))
        item.add_child(Node.s32_array('marker_list', profile.get_int_array('marker_list', 16, [-1] * 16)))
        item.add_child(Node.s32_array('title_list', profile.get_int_array('title_list', 160, [-1] * 160)))
        item.add_child(Node.s32_array('parts_list', profile.get_int_array('parts_list', 160, [-1] * 160)))
        item.add_child(Node.s32_array('emblem_list', profile.get_int_array('emblem_list', 96, [-1] * 96)))
        item.add_child(Node.s32_array('commu_list', profile.get_int_array('commu_list', 16, [-1] * 16)))

        new = Node.void('new')
        item.add_child(new)
        new.add_child(Node.s32_array('secret_list', profile.get_int_array('secret_list_new', 64, [-1] * 64)))
        new.add_child(Node.s32_array('theme_list', profile.get_int_array('theme_list_new', 16, [-1] * 16)))
        new.add_child(Node.s32_array('marker_list', profile.get_int_array('marker_list_new', 16, [-1] * 16)))

        # Add rivals to profile.
        rivallist = Node.void('rivallist')
        player.add_child(rivallist)

        links = self.data.local.user.get_links(self.game, self.version, userid)
        rivalcount = 0
        for link in links:
            if link.type != 'rival':
                continue

            rprofile = self.get_profile(link.other_userid)
            if rprofile is None:
                continue

            rival = Node.void('rival')
            rivallist.add_child(rival)
            rival.add_child(Node.s32('jid', rprofile.get_int('extid')))
            rival.add_child(Node.string('name', rprofile.get_str('name')))

            # This looks like a carry-over from prop's career and isn't displayed.
            career = Node.void('career')
            rival.add_child(career)
            career.add_child(Node.s16('level', 1))

            # Lazy way of keeping track of rivals, since we can only have 3
            # or the game with throw up.
            rivalcount += 1
            if rivalcount >= 3:
                break

        rivallist.set_attribute('count', str(rivalcount))

        lab_edit_seq = Node.void('lab_edit_seq')
        player.add_child(lab_edit_seq)
        lab_edit_seq.set_attribute('count', '0')

        # Full combo challenge
        entry = self.data.local.game.get_time_sensitive_settings(self.game, self.version, 'fc_challenge')
        if entry is None:
            entry = ValidatedDict()

        # Figure out if we've played these songs
        start_time, end_time = self.data.local.network.get_schedule_duration('daily')
        today_attempts = self.data.local.music.get_all_attempts(self.game, self.version, userid, entry.get_int('today', -1), timelimit=start_time)
        whim_attempts = self.data.local.music.get_all_attempts(self.game, self.version, userid, entry.get_int('whim', -1), timelimit=start_time)

        fc_challenge = Node.void('fc_challenge')
        player.add_child(fc_challenge)
        today = Node.void('today')
        fc_challenge.add_child(today)
        today.add_child(Node.s32('music_id', entry.get_int('today', -1)))
        today.add_child(Node.u8('state', 0x40 if len(today_attempts) > 0 else 0x0))
        whim = Node.void('whim')
        fc_challenge.add_child(whim)
        whim.add_child(Node.s32('music_id', entry.get_int('whim', -1)))
        whim.add_child(Node.u8('state', 0x40 if len(whim_attempts) > 0 else 0x0))

        # No news, ever.
        official_news = Node.void('official_news')
        player.add_child(official_news)
        news_list = Node.void('news_list')
        official_news.add_child(news_list)

        # Sane defaults for unknown/who cares nodes
        history = Node.void('history')
        player.add_child(history)
        history.set_attribute('count', '0')

        free_first_play = Node.void('free_first_play')
        player.add_child(free_first_play)
        free_first_play.add_child(Node.bool('is_available', False))

        # Player status for events
        event_info = Node.void('event_info')
        player.add_child(event_info)
        achievements = self.data.local.user.get_achievements(self.game, self.version, userid)
        event_completion: Dict[int, bool] = {}
        course_completion: Dict[int, ValidatedDict] = {}
        for achievement in achievements:
            if achievement.type == 'event':
                event_completion[achievement.id] = achievement.data.get_bool('is_completed')
            if achievement.type == 'course':
                course_completion[achievement.id] = achievement.data

        # JBox stuff
        jbox = Node.void('jbox')
        jboxdict = profile.get_dict('jbox')
        player.add_child(jbox)
        jbox.add_child(Node.s32('point', jboxdict.get_int('point')))
        emblem = Node.void('emblem')
        jbox.add_child(emblem)
        normal = Node.void('normal')
        emblem.add_child(normal)
        premium = Node.void('premium')
        emblem.add_child(premium)

        # Calculate a random index for normal and premium to give to player
        # as a gatcha.
        gameitems = self.data.local.game.get_items(self.game, self.version)
        normalemblems: Set[int] = set()
        premiumemblems: Set[int] = set()
        for gameitem in gameitems:
            if gameitem.type == 'emblem':
                if gameitem.data.get_int('rarity') in {1, 2, 3}:
                    normalemblems.add(gameitem.id)
                if gameitem.data.get_int('rarity') in {3, 4, 5}:
                    premiumemblems.add(gameitem.id)

        # Default to some emblems in case the catalog is not available.
        normalindex = 2
        premiumindex = 1
        if normalemblems:
            normalindex = random.sample(normalemblems, 1)[0]
        if premiumemblems:
            premiumindex = random.sample(premiumemblems, 1)[0]

        normal.add_child(Node.s16('index', normalindex))
        premium.add_child(Node.s16('index', premiumindex))

        # New Music stuff
        new_music = Node.void('new_music')
        player.add_child(new_music)

        navi = Node.void('navi')
        player.add_child(navi)
        navi.add_child(Node.u64('flag', profile.get_int('navi_flag')))

        # Gift list, maybe from other players?
        gift_list = Node.void('gift_list')
        player.add_child(gift_list)
        # If we had gifts, they look like this:
        #     <gift reason="??" kind="??">
        #         <id __type="s32">??</id>
        #     </gift>

        # Birthday event?
        born = Node.void('born')
        player.add_child(born)
        born.add_child(Node.s8('status', profile.get_int('born_status')))
        born.add_child(Node.s16('year', profile.get_int('born_year')))

        # More crap
        question_list = Node.void('question_list')
        player.add_child(question_list)

        # Union Battle
        union_battle = Node.void('union_battle')
        player.add_child(union_battle)
        union_battle.set_attribute('id', "0")
        union_battle.add_child(Node.s32("power", 0))

        # Some server node
        server = Node.void('server')
        player.add_child(server)

        # Another unknown gift list?
        eamuse_gift_list = Node.void('eamuse_gift_list')
        player.add_child(eamuse_gift_list)

        category_list = Node.void('category_list')
        player.add_child(category_list)

        # Clan Course List Progress
        clan_course_list = Node.void('course_list')
        player.add_child(clan_course_list)

        # Each course that we have completed has one of the following nodes.
        for course in self.__get_course_list():
            status_dict = course_completion.get(course['id'], ValidatedDict())
            status = 0
            status |= self.COURSE_STATUS_SEEN if status_dict.get_bool('seen') else 0
            status |= self.COURSE_STATUS_PLAYED if status_dict.get_bool('played') else 0
            status |= self.COURSE_STATUS_CLEARED if status_dict.get_bool('cleared') else 0

            clan_course = Node.void('course')
            clan_course_list.add_child(clan_course)
            clan_course.set_attribute('id', str(course['id']))
            clan_course.add_child(Node.s8('status', status))

        # Each category has one of the following nodes
        for categoryid in range(1, 7):
            category = Node.void('category')
            category_list.add_child(category)
            category.set_attribute('id', str(categoryid))
            category.add_child(Node.bool('is_display', True))

        # Drop list
        drop_list = Node.void('drop_list')
        player.add_child(drop_list)

        dropachievements: Dict[int, Achievement] = {}
        for achievement in achievements:
            if achievement.type == 'drop':
                dropachievements[achievement.id] = achievement

        for dropid in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            if dropid in dropachievements:
                dropdata = dropachievements[dropid].data
            else:
                dropdata = ValidatedDict()

            drop = Node.void('drop')
            drop_list.add_child(drop)
            drop.set_attribute('id', str(dropid))
            drop.add_child(Node.s32('exp', dropdata.get_int('exp', -1)))
            drop.add_child(Node.s32('flag', dropdata.get_int('flag', 0)))

            item_list = Node.void('item_list')
            drop.add_child(item_list)

            for itemid in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
                item = Node.void('item')
                item_list.add_child(item)
                item.set_attribute('id', str(itemid))
                item.add_child(Node.s32('num', dropdata.get_int(f'item_{itemid}')))

        department = Node.void('department')
        player.add_child(department)

        # Emo node added in festo
        emo_list = Node.void("emo_list")
        player.add_child(emo_list)

        # Fill in category
        fill_in_category = Node.void('fill_in_category')
        player.add_child(fill_in_category)
        normal = Node.void('normal')
        fill_in_category.add_child(normal)
        normal.add_child(Node.s32_array('no_gray_flag_list', profile.get_int_array('no_gray_flag_list', 16, [0] * 16)))
        normal.add_child(Node.s32_array('all_yellow_flag_list', profile.get_int_array('all_yellow_flag_list', 16, [0] * 16)))
        normal.add_child(Node.s32_array('full_combo_flag_list', profile.get_int_array('full_combo_flag_list', 16, [0] * 16)))
        normal.add_child(Node.s32_array('excellent_flag_list', profile.get_int_array('excellent_flag_list', 16, [0] * 16)))

        hard = Node.void('hard')
        fill_in_category.add_child(hard)
        hard.add_child(Node.s32_array('no_gray_flag_list', profile.get_int_array('hard_no_gray_flag_list', 16, [0] * 16)))
        hard.add_child(Node.s32_array('all_yellow_flag_list', profile.get_int_array('hard_all_yellow_flag_list', 16, [0] * 16)))
        hard.add_child(Node.s32_array('full_combo_flag_list', profile.get_int_array('hard_full_combo_flag_list', 16, [0] * 16)))
        hard.add_child(Node.s32_array('excellent_flag_list', profile.get_int_array('hard_excellent_flag_list', 16, [0] * 16)))

        # Daily Bonus
        daily_bonus_list = Node.void('daily_bonus_list')
        player.add_child(daily_bonus_list)

        # Tickets
        ticket_list = Node.void('ticket_list')
        player.add_child(ticket_list)

        return root

    def unformat_profile(self, userid: UserID, request: Node, oldprofile: ValidatedDict) -> ValidatedDict:
        newprofile = copy.deepcopy(oldprofile)
        data = request.child('data')

        # Grab system information
        sysinfo = data.child('info')

        # Grab player information
        player = data.child('player')

        # Grab result information
        result = data.child('result')

        # Grab last information. Lots of this will be filled in while grabbing scores
        last = newprofile.get_dict('last')
        if sysinfo is not None:
            last.replace_int('play_time', sysinfo.child_value('time_gameend'))
            last.replace_str('shopname', sysinfo.child_value('shopname'))
            last.replace_str('areaname', sysinfo.child_value('areaname'))

        # Grab player info for echoing back
        info = player.child('info')
        if info is not None:
            newprofile.replace_int('tune_cnt', info.child_value('tune_cnt'))
            newprofile.replace_int('save_cnt', info.child_value('save_cnt'))
            newprofile.replace_int('saved_cnt', info.child_value('saved_cnt'))
            newprofile.replace_int('fc_cnt', info.child_value('fc_cnt'))
            newprofile.replace_int('ex_cnt', info.child_value('ex_cnt'))
            newprofile.replace_int('clear_cnt', info.child_value('clear_cnt'))
            newprofile.replace_int('match_cnt', info.child_value('match_cnt'))
            newprofile.replace_int('beat_cnt', info.child_value('beat_cnt'))
            newprofile.replace_int('mynews_cnt', info.child_value('mynews_cnt'))

            newprofile.replace_int('bonus_tune_points', info.child_value('bonus_tune_points'))
            newprofile.replace_bool('is_bonus_tune_played', info.child_value('is_bonus_tune_played'))

        # Grab last settings
        lastnode = player.child('last')
        if lastnode is not None:
            last.replace_int('expert_option', lastnode.child_value('expert_option'))
            last.replace_int('sort', lastnode.child_value('sort'))
            last.replace_int('category', lastnode.child_value('category'))

            settings = lastnode.child('settings')
            if settings is not None:
                last.replace_int('matching', settings.child_value('matching'))
                last.replace_int('hazard', settings.child_value('hazard'))
                last.replace_int('hard', settings.child_value('hard'))
                last.replace_int('marker', settings.child_value('marker'))
                last.replace_int('theme', settings.child_value('theme'))
                last.replace_int('title', settings.child_value('title'))
                last.replace_int('parts', settings.child_value('parts'))
                last.replace_int('rank_sort', settings.child_value('rank_sort'))
                last.replace_int('combo_disp', settings.child_value('combo_disp'))
                last.replace_int_array('emblem', 5, settings.child_value('emblem'))

        # Grab unlock progress
        item = player.child('item')
        if item is not None:
            newprofile.replace_int_array('music_list', 64, item.child_value('music_list'))
            newprofile.replace_int_array('secret_list', 64, item.child_value('secret_list'))
            newprofile.replace_int_array('theme_list', 16, item.child_value('theme_list'))
            newprofile.replace_int_array('marker_list', 16, item.child_value('marker_list'))
            newprofile.replace_int_array('title_list', 160, item.child_value('title_list'))
            newprofile.replace_int_array('parts_list', 160, item.child_value('parts_list'))
            newprofile.replace_int_array('emblem_list', 96, item.child_value('emblem_list'))
            newprofile.replace_int_array('commu_list', 96, item.child_value('commu_list'))

            newitem = item.child('new')
            if newitem is not None:
                newprofile.replace_int_array('secret_list_new', 64, newitem.child_value('secret_list'))
                newprofile.replace_int_array('theme_list_new', 16, newitem.child_value('theme_list'))
                newprofile.replace_int_array('marker_list_new', 16, newitem.child_value('marker_list'))

        # Grab categories stuff
        fill_in_category = player.child('fill_in_category')
        fill_in_category_normal = fill_in_category.child('normal')
        if fill_in_category is not None:
            newprofile.replace_int_array('no_gray_flag_list', 16, fill_in_category_normal.child_value('no_gray_flag_list'))
            newprofile.replace_int_array('all_yellow_flag_list', 16, fill_in_category_normal.child_value('all_yellow_flag_list'))
            newprofile.replace_int_array('full_combo_flag_list', 16, fill_in_category_normal.child_value('full_combo_flag_list'))
            newprofile.replace_int_array('excellent_flag_list', 16, fill_in_category_normal.child_value('excellent_flag_list'))
        fill_in_category_hard = fill_in_category.child('hard')
        if fill_in_category is not None:
            newprofile.replace_int_array('hard_no_gray_flag_list', 16, fill_in_category_hard.child_value('no_gray_flag_list'))
            newprofile.replace_int_array('hard_all_yellow_flag_list', 16, fill_in_category_hard.child_value('all_yellow_flag_list'))
            newprofile.replace_int_array('hard_full_combo_flag_list', 16, fill_in_category_hard.child_value('full_combo_flag_list'))
            newprofile.replace_int_array('hard_excellent_flag_list', 16, fill_in_category_hard.child_value('excellent_flag_list'))
        # jbox stuff
        jbox = player.child('jbox')
        jboxdict = newprofile.get_dict('jbox')
        if jbox is not None:
            jboxdict.replace_int('point', jbox.child_value('point'))
            emblemtype = jbox.child_value('emblem/type')
            index = jbox.child_value('emblem/index')
            if emblemtype == self.JBOX_EMBLEM_NORMAL:
                jboxdict.replace_int('normal_index', index)
            elif emblemtype == self.JBOX_EMBLEM_PREMIUM:
                jboxdict.replace_int('premium_index', index)
        newprofile.replace_dict('jbox', jboxdict)

        # Drop list
        drop_list = player.child('drop_list')
        if drop_list is not None:
            for drop in drop_list.children:
                try:
                    dropid = int(drop.attribute('id'))
                except TypeError:
                    # Unrecognized drop
                    continue
                exp = drop.child_value('exp')
                flag = drop.child_value('flag')
                items: Dict[int, int] = {}

                item_list = drop.child('item_list')
                if item_list is not None:
                    for item in item_list.children:
                        try:
                            itemid = int(item.attribute('id'))
                        except TypeError:
                            # Unrecognized item
                            continue
                        items[itemid] = item.child_value('num')

                olddrop = self.data.local.user.get_achievement(
                    self.game,
                    self.version,
                    userid,
                    dropid,
                    'drop',
                )

                if olddrop is None:
                    # Create a new event structure for this
                    olddrop = ValidatedDict()

                olddrop.replace_int('exp', exp)
                olddrop.replace_int('flag', flag)
                for itemid, num in items.items():
                    olddrop.replace_int(f'item_{itemid}', num)

                # Save it as an achievement
                self.data.local.user.put_achievement(
                    self.game,
                    self.version,
                    userid,
                    dropid,
                    'drop',
                    olddrop,
                )

        # event stuff
        newprofile.replace_int('event_flag', player.child_value('event_flag'))
        event_info = player.child('event_info')
        if event_info is not None:
            for child in event_info.children:
                try:
                    eventid = int(child.attribute('type'))
                except TypeError:
                    # Event is empty
                    continue
                is_completed = child.child_value('is_completed')

                # Figure out if we should update the rating/scores or not
                oldevent = self.data.local.user.get_achievement(
                    self.game,
                    self.version,
                    userid,
                    eventid,
                    'event',
                )

                if oldevent is None:
                    # Create a new event structure for this
                    oldevent = ValidatedDict()

                oldevent.replace_bool('is_completed', is_completed)

                # Save it as an achievement
                self.data.local.user.put_achievement(
                    self.game,
                    self.version,
                    userid,
                    eventid,
                    'event',
                    oldevent,
                )

        # Still don't know what this is for lol
        newprofile.replace_int('navi_flag', player.child_value('navi/flag'))

        # Grab scores and save those
        if result is not None:
            for tune in result.children:
                if tune.name != 'tune':
                    continue
                result = tune.child('player')

                # Fix mapping to song IDs for the song with seven billion charts
                # due to the prefecture unlock event.
                songid = tune.child_value('music')
                if songid in self.FIVE_PLAYS_UNLOCK_EVENT_SONG_IDS:
                    songid = 80000301

                timestamp = tune.child_value('timestamp') / 1000
                chart = int(result.child('score').attribute('seq'))
                points = result.child_value('score')
                flags = int(result.child('score').attribute('clear'))
                combo = int(result.child('score').attribute('combo'))
                ghost = result.child_value('mbar')
                music_rate = result.child_value('music_rate')
                is_hard_mode = bool(result.child_value('is_hard_mode'))

                stats = {
                    'perfect': result.child_value('nr_perfect'),
                    'great': result.child_value('nr_great'),
                    'good': result.child_value('nr_good'),
                    'poor': result.child_value('nr_poor'),
                    'miss': result.child_value('nr_miss'),
                }

                # Miscelaneous last data for echoing to profile get
                last.replace_int('music_id', songid)
                last.replace_int('seq_id', chart)

                mapping = {
                    self.GAME_FLAG_BIT_CLEARED: self.PLAY_MEDAL_CLEARED,
                    self.GAME_FLAG_BIT_FULL_COMBO: self.PLAY_MEDAL_FULL_COMBO,
                    self.GAME_FLAG_BIT_EXCELLENT: self.PLAY_MEDAL_EXCELLENT,
                    self.GAME_FLAG_BIT_NEARLY_FULL_COMBO: self.PLAY_MEDAL_NEARLY_FULL_COMBO,
                    self.GAME_FLAG_BIT_NEARLY_EXCELLENT: self.PLAY_MEDAL_NEARLY_EXCELLENT,
                }

                # Figure out the highest medal based on bits passed in
                medal = self.PLAY_MEDAL_FAILED
                for bit in mapping:
                    if flags & bit > 0:
                        medal = max(medal, mapping[bit])

                self.update_score(userid, timestamp, songid, chart, points, medal,
                                  combo, ghost, stats, music_rate, is_hard_mode)

        # Born stuff
        born = player.child('born')
        if born is not None:
            newprofile.replace_int('born_status', born.child_value('status'))
            newprofile.replace_int('born_year', born.child_value('year'))

        # Clan course saving
        clan_course_list = player.child('course_list')
        if clan_course_list is not None:
            for course in clan_course_list.children:
                if course.name != 'course':
                    continue

                courseid = int(course.attribute('id'))
                status = course.child_value('status')
                is_seen = (status & self.COURSE_STATUS_SEEN) != 0
                is_played = (status & self.COURSE_STATUS_PLAYED) != 0

                # Update seen status and played status
                oldcourse = self.data.local.user.get_achievement(
                    self.game,
                    self.version,
                    userid,
                    courseid,
                    'course',
                )

                if oldcourse is None:
                    # Create a new course structure for this
                    oldcourse = ValidatedDict()

                oldcourse.replace_bool('seen', oldcourse.get_bool('seen') or is_seen)
                oldcourse.replace_bool('played', oldcourse.get_bool('played') or is_played)

                # Save it as an achievement
                self.data.local.user.put_achievement(
                    self.game,
                    self.version,
                    userid,
                    courseid,
                    'course',
                    oldcourse,
                )

        select_course = player.child('select_course')
        if select_course is not None:
            try:
                courseid = int(select_course.attribute('id'))
            except Exception:
                courseid = 0
            cleared = select_course.child_value('is_cleared')

            if courseid > 0 and cleared:
                # Update course cleared status
                oldcourse = self.data.local.user.get_achievement(
                    self.game,
                    self.version,
                    userid,
                    courseid,
                    'course',
                )

                if oldcourse is None:
                    # Create a new course structure for this
                    oldcourse = ValidatedDict()

                oldcourse.replace_bool('cleared', True)

                # Save it as an achievement
                self.data.local.user.put_achievement(
                    self.game,
                    self.version,
                    userid,
                    courseid,
                    'course',
                    oldcourse,
                )

        # Save back last information gleaned from results
        newprofile.replace_dict('last', last)

        # Keep track of play statistics
        self.update_play_statistics(userid)

        return newprofile
