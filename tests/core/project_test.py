import os

import pytest

from golem.core import test, page, suite
from golem.core.project import Project, create_project, validate_project_element_name


class TestCreateProject:

    def test_create_project(self, testdir_session, test_utils):
        testdir_session.activate()
        project_name = test_utils.random_string()
        create_project(project_name)
        path = Project(project_name).path
        listdir = os.listdir(path)
        files = [n for n in listdir if os.path.isfile(os.path.join(path, n))]
        dirs = [n for n in listdir if os.path.isdir(os.path.join(path, n))]
        if '.DS_Store' in files:
            files.remove('.DS_Store')
        assert len(files) == 5
        # verify files
        assert '__init__.py' in files
        assert 'extend.py' in files
        assert 'environments.json' in files
        assert 'settings.json' in files
        assert 'secrets.json' in files
        # verify directories
        assert len(dirs) == 4
        # verify the test dir contains the correct directories
        assert 'pages' in dirs
        assert 'reports' in dirs
        assert 'tests' in dirs
        assert 'suites' in dirs


class TestTestTree:

    def test_test_tree(self, project_function):
        _, project = project_function.activate()
        test.create_test(project, 'subdir1.subdir2.test3')
        test.create_test(project, 'subdir1.test2')
        test.create_test(project, 'test1')
        tests = Project(project).test_tree
        expected = {
            'type': 'directory',
            'name': 'tests',
            'dot_path': '.',
            'sub_elements': [
                {
                    'type': 'directory',
                    'name': 'subdir1',
                    'dot_path': 'subdir1',
                    'sub_elements': [
                        {
                            'type': 'directory',
                            'name': 'subdir2',
                            'dot_path': 'subdir1.subdir2',
                            'sub_elements': [
                                {
                                    'type': 'file',
                                    'name': 'test3',
                                    'dot_path': 'subdir1.subdir2.test3',
                                    'sub_elements': []
                                }
                            ]
                        },
                        {
                            'type': 'file',
                            'name': 'test2',
                            'dot_path': 'subdir1.test2', 'sub_elements': []
                        }
                    ]
                },
                {
                    'type': 'file',
                    'name': 'test1',
                    'dot_path': 'test1',
                    'sub_elements': []
                }
            ]
        }
        assert tests == expected

    def test_test_tree_no_tests(self, project_function):
        _, project = project_function.activate()
        tests = Project(project).test_tree
        expected = {'type': 'directory', 'name': 'tests', 'dot_path': '.', 'sub_elements': []}
        assert tests == expected


class TestPageTree:

    def test_page_tree(self, project_function):
        _, project = project_function.activate()
        page.create_page(project, 'subdir1.subdir2.test3')
        page.create_page(project, 'subdir1.test2')
        page.create_page(project, 'test1')
        pages = Project(project).page_tree
        expected = {
            'type': 'directory',
            'name': 'pages',
            'dot_path': '.',
            'sub_elements': [
                {
                    'type': 'directory',
                    'name': 'subdir1',
                    'dot_path': 'subdir1',
                    'sub_elements': [
                        {
                            'type': 'directory',
                            'name': 'subdir2',
                            'dot_path': 'subdir1.subdir2',
                            'sub_elements': [
                            {
                                'type': 'file',
                                'name': 'test3',
                                'dot_path': 'subdir1.subdir2.test3',
                                'sub_elements': []
                            }
                        ]
                        },
                        {
                            'type': 'file',
                            'name': 'test2',
                            'dot_path': 'subdir1.test2',
                            'sub_elements': []
                        }
                    ]
                },
                {
                    'type': 'file',
                    'name': 'test1',
                    'dot_path': 'test1',
                    'sub_elements': []
                }
            ]
        }
        assert pages == expected

    def test_page_tree_no_pages(self, project_function):
        _, project = project_function.activate()
        pages = Project(project).page_tree
        expected = {'type': 'directory', 'name': 'pages', 'dot_path': '.', 'sub_elements': []}
        assert pages == expected


class TestSuiteTree:

    def test_suite_tree(self, project_function):
        _, project = project_function.activate()
        suite.create_suite(project, 'suite1')
        suite.create_suite(project, 'suite2')
        suites = Project(project).suite_tree
        expected_result = {
            'type': 'directory',
            'name': 'suites',
            'dot_path': '.',
            'sub_elements': [
                {
                    'type': 'file',
                    'name': 'suite1',
                    'dot_path': 'suite1',
                    'sub_elements': []
                },
                {
                    'type': 'file',
                    'name': 'suite2',
                    'dot_path': 'suite2',
                    'sub_elements': []
                }
            ]
        }
        assert suites == expected_result

    def test_suite_tree_no_suites(self, project_function):
        _, project = project_function.activate()
        suites = Project(project).suite_tree
        expected = {'type': 'directory', 'name': 'suites', 'dot_path': '.', 'sub_elements': []}
        assert suites == expected


class TestGetTests:

    def test_get_tests(self, project_function, test_utils):
        _, project_name = project_function.activate()
        test_utils.create_test(project_name, 'test_one')
        test_utils.create_test(project_name, 'foo.test_two')
        test_utils.create_test(project_name, 'foo.bar.test_three')
        test_utils.create_test(project_name, 'foo.bar.baz.test_four')
        project = Project(project_name)
        tests = project.tests()
        expected = ['test_one', 'foo.test_two', 'foo.bar.test_three', 'foo.bar.baz.test_four']
        assert tests == expected
        tests = project.tests('foo')
        expected = ['foo.test_two', 'foo.bar.test_three', 'foo.bar.baz.test_four']
        assert tests == expected
        tests = project.tests('foo/')
        assert tests == expected
        expected = ['foo.bar.test_three', 'foo.bar.baz.test_four']
        tests = project.tests('foo/bar')
        assert tests == expected


class TestHasTests:

    def test_project_has_tests(self, project_function, test_utils):
        _, project = project_function.activate()
        assert not Project(project).has_tests
        test_utils.create_test(project, 'test01')
        assert Project(project).has_tests


class TestCreatePackagesForElement:

    def test_create_packages_for_element(self, project_session, test_utils):
        _, project = project_session.activate()
        project_obj = Project(project)
        random_dir = test_utils.random_string()
        elem_name = '{}.{}'.format(random_dir, test_utils.random_string())
        project_obj.create_packages_for_element(elem_name, 'test')
        dir_path = os.path.join(project_obj.test_directory_path, random_dir)
        assert os.path.isdir(dir_path)
        init_path = os.path.join(dir_path, '__init__.py')
        assert os.path.isfile(init_path)
        # element without parent subdirectories
        elem_name = test_utils.random_string()
        project_obj.create_packages_for_element(elem_name, 'test')
        dir_path = os.path.join(project_obj.test_directory_path, elem_name)
        assert not os.path.isdir(dir_path)
        # page
        random_dir = test_utils.random_string()
        elem_name = '{}.{}'.format(random_dir, test_utils.random_string())
        project_obj.create_packages_for_element(elem_name, 'page')
        dir_path = os.path.join(project_obj.page_directory_path, random_dir)
        assert os.path.isdir(dir_path)
        init_path = os.path.join(dir_path, '__init__.py')
        assert os.path.isfile(init_path)
        # suite
        random_dir = test_utils.random_string()
        elem_name = '{}.{}'.format(random_dir, test_utils.random_string())
        project_obj.create_packages_for_element(elem_name, 'suite')
        dir_path = os.path.join(project_obj.suite_directory_path, random_dir)
        assert os.path.isdir(dir_path)
        init_path = os.path.join(dir_path, '__init__.py')
        assert os.path.isfile(init_path)


class TestCreateDirectories:

    def test_create_directories(self, project_session, test_utils):
        _, project = project_session.activate()
        project_obj = Project(project)
        dir_name = test_utils.random_string()
        # test
        errors = project_obj.create_directories(dir_name, 'test')
        assert errors == []
        assert os.path.isdir(os.path.join(project_obj.test_directory_path, dir_name))
        # page
        errors = project_obj.create_directories(dir_name, 'page')
        assert errors == []
        assert os.path.isdir(os.path.join(project_obj.page_directory_path, dir_name))
        # suite
        errors = project_obj.create_directories(dir_name, 'suite')
        assert errors == []
        assert os.path.isdir(os.path.join(project_obj.suite_directory_path, dir_name))
        # three directory levels
        part_one = test_utils.random_string()
        part_two = test_utils.random_string()
        part_three = test_utils.random_string()
        dir_name = '{}.{}.{}'.format(part_one, part_two, part_three)
        errors = project_obj.create_directories(dir_name, 'suite')
        assert errors == []
        path = os.path.join(project_obj.suite_directory_path, part_one, part_two, part_three)
        assert os.path.isdir(path)

    def test_create_directories_already_exists(self, project_session, test_utils):
        _, project = project_session.activate()
        project_obj = Project(project)
        dir_name = test_utils.random_string()
        errors = project_obj.create_directories(dir_name, 'test')
        assert errors == []
        assert os.path.isdir(os.path.join(project_obj.test_directory_path, dir_name))
        errors = project_obj.create_directories(dir_name, 'test')
        assert errors == ['A directory with that name already exists']
        assert os.path.isdir(os.path.join(project_obj.test_directory_path, dir_name))

    def test_create_directories_invalid_name(self, project_session):
        _, project = project_session.activate()
        project_obj = Project(project)
        errors = project_obj.create_directories('test-directory', 'test')
        assert errors == ['Only letters, numbers and underscores are allowed']


class TestValidateProjectElementName:

    names = [
        'filename',
        'file_name',
        'file_name123',
        'a.valid.filename',
        'this.is.a_valid.file_name'
    ]

    empty_dirs = [
        '.name',
        '.file.name',
        'file..name',
        'fi_le..na_me'
    ]

    empty_names = [
        '',
        'test.',
        'this.is.a.test.'
    ]

    invalid_chars = [
        'tes t',
        'te-st',
        't-e-s-t',
        'te$t',
        'te/st',
        '/test',
        'test/',
        '\\test',
        'te-st.test'
    ]

    @pytest.mark.parametrize('name', names)
    def test_validate_project_element_name(self, name):
        errors = validate_project_element_name(name)
        assert errors == []

    @pytest.mark.parametrize('name', empty_dirs)
    def test_validate_project_element_name_empty_dir(self, name):
        errors = validate_project_element_name(name)
        assert errors == ['Directory name cannot be empty']

    @pytest.mark.parametrize('name', empty_names)
    def test_validate_project_element_name_empty_name(self, name):
        errors = validate_project_element_name(name)
        assert errors == ['File name cannot be empty']

    @pytest.mark.parametrize('name', invalid_chars)
    def test_validate_project_element_name_invalid_chars(self, name):
        errors = validate_project_element_name(name)
        assert errors == ['Only letters, numbers and underscores are allowed']
