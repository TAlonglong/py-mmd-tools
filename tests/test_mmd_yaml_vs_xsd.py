import os
import yaml
from pkg_resources import resource_string
import xmltodict
import unittest

import py_mmd_tools

class TestMDDElementsInYAMLAndXSD(unittest.TestCase):

    def setUp(self):
        xml_file = os.path.join(os.environ['MMD_PATH'], 'xsd/mmd.xsd')
        with open(xml_file) as xml:
            self.mmd_xml = xmltodict.parse(xml.read())
        self.mmd_yaml = yaml.load(resource_string(py_mmd_tools.__name__, 'mmd_elements.yaml'), Loader=yaml.FullLoader)

    def check_elements(self, elements, type_defs = {}):
        for elem in elements:
            if elem['@type'].startswith('mmd:'):
                type_defs[elem['@type']] = [elem['@name']]
            self.assertIn(elem['@name'], self.mmd_yaml.keys())
            # Skipping the following tests because there are intentional differences:
            #self.assertEqual(elem['@maxOccurs'], self.mmd_yaml[elem['@name']]['maxOccurs'], msg=elem['@name'])
            #self.assertEqual(elem['@minOccurs'], self.mmd_yaml[elem['@name']]['minOccurs'], msg=elem['@name'])
        return type_defs

    def check_sub_elements(self, type_defs):
        # Create list of sub elements in type_defs if there are any
        parallel_sub_type_defs = []
        # Loop elements in list type_defs
        for elem_name in type_defs.keys():
            #print(type_defs[elem_name])
            lll = [x for x in self.mmd_xml['xs:schema']['xs:complexType'] if x['@name']==elem_name[4:]] #.strip('mmd:')]
            if lll:
                ll = lll[0]
            else:
                continue
            if not 'xs:sequence' in ll.keys():
                continue
            if not 'xs:element' in ll['xs:sequence'].keys():
                continue
            elements = ll['xs:sequence']['xs:element']
            if not type(elements)==list:
                elements = [elements]
            sub_type_defs = {}
            for elem in elements:
                yaml_entry = self.mmd_yaml
                yaml_loginfo = "self.mmd_yaml"
                for tde_name in type_defs[elem_name]:
                    yaml_entry = yaml_entry[tde_name]
                    yaml_loginfo = yaml_loginfo + "['%s']" %tde_name
                self.assertIn(elem['@name'], yaml_entry.keys(), msg='%s: %s' %(yaml_loginfo, elem['@name']))
                if elem['@type'].startswith('mmd:'):
                    tmp = type_defs[elem_name].copy()
                    tmp.append(elem['@name'])
                    sub_type_defs[elem['@type']] = tmp
            if sub_type_defs:
                parallel_sub_type_defs.append(sub_type_defs)
        return parallel_sub_type_defs

    def test_mmd_element(self):
        # Get mmd_type elements
        ll = [x for x in self.mmd_xml['xs:schema']['xs:complexType'] if x['@name']=='mmd_type'][0]
        self.assertEqual(ll['@name'], 'mmd_type')

        # Loop MMD elements and check that they are present in the yaml file
        type_defs = self.check_elements(ll['xs:sequence']['xs:element'])
        # Loop elements under xs:choice
        type_defs = self.check_elements(ll['xs:sequence']['xs:choice']['xs:element'])
        
        sub_type_defs = self.check_sub_elements(type_defs)
        # Loop elements in list sub_type_defs
        for sub_type_def in sub_type_defs:
            sub_sub_type_defs = self.check_sub_elements(sub_type_def)
            for sub_sub_type_def in sub_sub_type_defs:
                sub_sub_sub_type_defs = self.check_sub_elements(sub_sub_type_def)

if __name__ == '__main__':
    unittest.main()
