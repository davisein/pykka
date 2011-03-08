import unittest
import uuid

from pykka.actor import ThreadingActor
from pykka.gevent import GeventActor


class AnActor(object):
    def __init__(self):
        self.post_start_was_executed = False

    def post_start(self):
        self.post_start_was_executed = True

    def react(self, message):
        if message.get('command') == 'get post_start_was_executed':
            return self.post_start_was_executed
        else:
            super(AnActor, self).react(message)


class ActorTest(object):
    def setUp(self):
        self.unstarted_actor = self.AnActor()
        self.actor = self.AnActor.start()
        self.actors = [self.AnActor.start() for _ in range(3)]

    def tearDown(self):
        for actor in self.actors:
            actor.stop()

    def test_sending_unexpected_message_raises_not_implemented_error(self):
        try:
            self.actor.send_request_reply({'unhandled': 'message'})
            self.fail('Should throw NotImplementedError')
        except NotImplementedError:
            pass

    def test_actor_has_an_uuid4_based_urn(self):
        self.assertEqual(4, uuid.UUID(self.actors[0].actor_urn).version)

    def test_actor_has_unique_uuid(self):
        self.assertNotEqual(self.actors[0].actor_urn, self.actors[1].actor_urn)
        self.assertNotEqual(self.actors[1].actor_urn, self.actors[2].actor_urn)
        self.assertNotEqual(self.actors[2].actor_urn, self.actors[0].actor_urn)

    def test_str_on_raw_actor_contains_actor_class_name(self):
        self.assert_('AnActor' in str(self.unstarted_actor))

    def test_str_on_raw_actor_contains_actor_urn(self):
        self.assert_(self.unstarted_actor.actor_urn
            in str(self.unstarted_actor))

    def test_post_start_is_executed_before_first_message_is_processed(self):
        self.assertFalse(self.unstarted_actor.post_start_was_executed)
        self.assertTrue(self.actor.send_request_reply(
            {'command': 'get post_start_was_executed'}))


class GeventActorTest(ActorTest, unittest.TestCase):
    class AnActor(AnActor, GeventActor): pass


class ThreadingActorTest(ActorTest, unittest.TestCase):
    class AnActor(AnActor, ThreadingActor): pass
