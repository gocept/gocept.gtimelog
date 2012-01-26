# -*- coding: utf-8 -*-
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

from gocept.gtimelog.collmex import match, MatchableObject
import gocept.collmex.collmex
import gocept.collmex.model
import gocept.gtimelog.core
import unittest


TEST_MATCHES = [
    "administration",
    "I_ZODBIndexing",
    "I_ZEO_Raid",
    "I_zope3-12345",
    "I_host_ing-12345",
    "General activities",
    "Programming application",
]


class CollmexMock(object):

    def __init__(self, *args, **kw):
        self.projects = []
        projects = [
            {'Bezeichnung': u'I_ZODBIndexing',
             'Projektnummer': u'1',
             'Abgeschlossen': u'0',
             'Produktnummer': u'3',
             'Satz Bezeichnung': u'Programming application',
             'Satz Nr': u'1'},
            {'Bezeichnung': u'I_ZODBIndexing',
             'Projektnummer': u'1',
             'Abgeschlossen': u'0',
             'Produktnummer': u'2',
             'Satz Bezeichnung': u'Research',
             'Satz Nr': u'2'},
            {'Bezeichnung': u'I_ZODBIndexing',
             'Projektnummer': u'1',
             'Abgeschlossen': u'0',
             'Produktnummer': u'1',
             'Satz Bezeichnung': u'Consultancy',
             'Satz Nr': u'3'},
            {'Bezeichnung': u'administration',
             'Projektnummer': u'2',
             'Abgeschlossen': u'0',
             'Produktnummer': u'3',
             'Satz Bezeichnung': u'Programming application',
             'Satz Nr': u'1'},
            {'Bezeichnung': u'old',
             'Projektnummer': u'3',
             'Abgeschlossen': u'1',
             'Produktnummer': u'3',
             'Satz Bezeichnung': u'Programming application',
             'Satz Nr': u'1'},
        ]
        for p in projects:
            project = gocept.collmex.model.Project()
            project.update(p)
            self.projects.append(project)

    def get_projects(self):
        return self.projects

    def get_products(self):
        product = gocept.collmex.model.Product()
        product['Produktnummer'] = '3'
        product['Bezeichnung Eng'] = 'Programming application in english'
        return [product]


class CollmexTest(unittest.TestCase):

    def setUp(self):
        super(CollmexTest, self).setUp()
        self.old_collmex = gocept.collmex.collmex.Collmex
        gocept.collmex.collmex.Collmex = CollmexMock

    def tearDown(self):
        gocept.collmex.collmex.Collmex = self.old_collmex
        super(CollmexTest, self).tearDown()

    def test_import_projects_and_tasks(self):
        collmex = gocept.gtimelog.collmex.Collmex(
            gocept.gtimelog.core.Settings())
        projects = collmex.projects
        self.assertEquals(2, len(projects))
        zodbi = projects[0]
        self.assertEquals('I_ZODBIndexing', zodbi.match_string)
        self.assertEquals('1', zodbi.id)
        tasks = zodbi.references
        self.assertEquals(4, len(tasks))
        self.assertEquals('Research', tasks[2].match_string)
        self.assertEquals('2', tasks[2].id)
        self.assertEquals('Programming application in english',
                          tasks[1].match_string)
        self.assertEquals('1', tasks[1].id)

    def test_split_timelog_entry(self):
        collmex = gocept.gtimelog.collmex.Collmex(
            gocept.gtimelog.core.Settings())

        entry = 'I_ZODB: Research: Testing the timelog split'
        r = collmex.mapEntry(entry)
        self.assertEquals('I_ZODBIndexing', r[0].match_string)
        self.assertEquals('Research', r[1].match_string)
        self.assertEquals('Testing the timelog split', r[2])

        invalid_entries = [
            'administration: Research: Did something stupid.',
            'administration: This is not a valid entry.',
            'foo: bar: This is not a valid entry.',
        ]
        for entry in invalid_entries:
            self.assertRaises(ValueError, collmex.mapEntry, entry)


class MatchableTest(unittest.TestCase):

    def setUp(self):
        super(MatchableTest, self).setUp()
        self.matchables = [MatchableObject(p, None) for p in TEST_MATCHES]

    def match(self, match_string):
        return match(match_string, self.matchables).match_string

    def test_match_exact(self):
        for machable_string in TEST_MATCHES:
            self.assertEquals(machable_string, self.match(machable_string))

    def test_match_simple(self):
        self.assertEquals('I_zope3-12345', self.match('I_zope3'))
        self.assertEquals('I_zope3-12345', self.match('i_zope3'))

    def test_match_transformed(self):
        self.assertEquals('I_zope3-12345', self.match('I zope3'))
        self.assertEquals('I_zope3-12345', self.match('i zope3'))
        self.assertEquals('I_ZODBIndexing', self.match('I_ZODB'))
        self.assertRaises(ValueError, self.match, 'I_')

    def test_no_match(self):
        self.assertRaises(ValueError, self.match, 'foo')
        self.assertRaises(ValueError, self.match, 'Indexing')
