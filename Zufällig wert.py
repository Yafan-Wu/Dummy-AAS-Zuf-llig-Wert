import xml.etree.ElementTree as ET
import json
import random
from pathlib import Path

# Only process HC10_AAS.xml file
file_path = "/Users/yafanwu/Downloads/HC10_AAS.xml"

def parse_hc10_capabilities(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    ns = {'aas': 'https://admin-shell.io/aas/3/0'}

    capabilities = []

    for capability_SM in root.findall(".//aas:submodel", ns):
        capability_SM_value = capability_SM.find(".//aas:value", ns)
        if capability_SM_value is not None and "https://admin-shell.io/idta/CapabilityDescription/1/0/Submodel" in capability_SM_value.text:
            for capability_sets in capability_SM.findall("aas:submodelElements/aas:submodelElementCollection", ns):
                for capability_container in capability_sets.findall("aas:value/aas:submodelElementCollection", ns):
                    for capability_element in capability_container.findall("aas:value/aas:capability", ns):
                        if capability_element is not None:
                            capability_element_name = capability_element.find("aas:idShort", ns)
                            capability_element_reference = capability_element.find("aas:supplementalSemanticIds//aas:value", ns)
                            capability = {
                                'capability': [],
                                'properties': [],
                                'generalized_by': [],
                                'realized_by': []
                            }

                            capability['capability'].append({
                                'capability_name': capability_element_name.text,
                                'capability_comment': "<VAR>",
                                'capability_ID': capability_element_reference.text
                            })

                            # Properties
                            for property_sets in capability_container.findall(".//aas:submodelElementCollection", ns):
                                property_sets_value = property_sets.find(".//aas:value", ns)
                                if property_sets_value is not None and "https://admin-shell.io/idta/CapabilityDescription/PropertySet/1/0" in property_sets_value.text:
                                    for property_container in property_sets.findall(".//aas:submodelElementCollection", ns):
                                        property_type_range = property_container.find("aas:value/aas:range", ns)
                                        if property_type_range is not None:

                                            prop_name = property_type_range.find("aas:idShort", ns)
                                            prop_id = property_type_range.find("aas:supplementalSemanticIds//aas:value", ns)
                                            unit = property_type_range.find("aas:embeddedDataSpecifications//aas:value", ns)
                                            vtype = property_type_range.find("aas:valueType", ns)
                                            min_val = property_type_range.find("aas:min", ns)
                                            max_val = property_type_range.find("aas:max", ns)
                                            prop_relBy = property_container.find("aas:value/aas:relationshipElement/aas:second//aas:value", ns)

                                            prop_entry = {
                                                'property_name': prop_name.text if prop_name is not None else "",
                                                'property_comment': "<VAR>",
                                                'property_ID': prop_id.text if prop_id is not None else "",
                                                'property_unit': unit.text if unit is not None else "",
                                                'valueType': vtype.text if vtype is not None else "",
                                                'valueMin': min_val.text if min_val is not None else "",
                                                'valueMax': max_val.text if max_val is not None else "",
                                                'propertyRealizedBy': prop_relBy.text if prop_relBy is not None else "",
                                                'property_constraint': []
                                            }

                                            # Search for optional Constraints
                                            for capability_relations in capability_container.findall(".//aas:submodelElementCollection", ns):
                                                capability_relations_semantic_id = capability_relations.find("aas:semanticId//aas:value", ns)
                                                if capability_relations_semantic_id is not None and "https://admin-shell.io/idta/CapabilityDescription/CapabilityRelations/1/0" in capability_relations_semantic_id.text:

                                                    for constraint_sets in capability_relations.findall("aas:value/aas:submodelElementCollection", ns):
                                                        constraint_set_semantic_id = constraint_sets.find("aas:semanticId//aas:value", ns)
                                                        if constraint_set_semantic_id is not None and "https://admin-shell.io/idta/CapabilityDescription/ConstraintSet/1/0" in constraint_set_semantic_id.text:

                                                            for constraint_set in constraint_sets.findall("aas:value/aas:submodelElementCollection", ns):
                                                                constraint_set_semantic_id = constraint_set.find("aas:semanticId//aas:value", ns)
                                                                if constraint_set_semantic_id is not None and "https://admin-shell.io/idta/CapabilityDescription/PropertyConstraintContainer/1/0" in constraint_set_semantic_id.text:

                                                                    for relationship_constraint in constraint_set.findall("aas:value/aas:submodelElementCollection/aas:value/aas:relationshipElement", ns):
                                                                        second_keys = relationship_constraint.find("aas:second/aas:keys", ns)
                                                                        if second_keys is not None:
                                                                            key_elements = second_keys.findall("aas:key", ns)
                                                                            if key_elements:
                                                                                last_key = key_elements[-1]
                                                                                last_value = last_key.find("aas:value", ns)
                                                                                if last_value is not None and last_value.text == prop_name.text:

                                                                                    # Initialize collection variables for this property
                                                                                    constraint_type = None
                                                                                    conditional_type = None
                                                                                    property_constraint_ID = None
                                                                                    property_constraint_unit = None
                                                                                    property_constraint_value = None

                                                                                    # Now iterate through all properties of this ConstraintContainer
                                                                                    for property_elements in constraint_set.findall("aas:value/aas:property", ns):
                                                                                        property_element_semantic_id = property_elements.find("aas:semanticId//aas:value", ns)

                                                                                        if property_element_semantic_id is not None:
                                                                                            sid_text = property_element_semantic_id.text

                                                                                            if "https://admin-shell.io/idta/CapabilityDescription/ConstraintType/1/0" in sid_text:
                                                                                                constraint_type_value = property_elements.find("aas:value", ns)
                                                                                                constraint_type = constraint_type_value.text if constraint_type_value is not None else ""

                                                                                            elif "https://admin-shell.io/idta/CapabilityDescription/PropertyConditionalType/1/0" in sid_text:
                                                                                                conditional_type_value = property_elements.find("aas:value", ns)
                                                                                                conditional_type = conditional_type_value.text if conditional_type_value is not None else ""

                                                                                            elif "https://admin-shell.io/idta/CapabilityDescription/PropertyConstraintType/BasicConstraint/1/0" in sid_text:
                                                                                                constraint_ID_value = property_elements.find("aas:supplementalSemanticIds//aas:value", ns)
                                                                                                unit_value = property_elements.find("aas:embeddedDataSpecifications//aas:value", ns)
                                                                                                qualifier_value = property_elements.find("aas:qualifiers//aas:value", ns)
                                                                                                constraint_value = property_elements.find("aas:value", ns)

                                                                                                property_constraint_ID = constraint_ID_value.text if constraint_ID_value is not None else ""
                                                                                                property_constraint_unit = unit_value.text if unit_value is not None else ""

                                                                                                if qualifier_value is not None and qualifier_value.text == "GREATER_EQUAL_1":
                                                                                                    property_constraint_value = ">=" + (constraint_value.text if constraint_value is not None else "")
                                                                                                else:
                                                                                                    property_constraint_value = constraint_value.text if constraint_value is not None else ""

                                                                                    # Create a single constraint object after collecting everything
                                                                                    constraint = {
                                                                                        'conditional_type': conditional_type if conditional_type else "",
                                                                                        'constraint_type': constraint_type if constraint_type else "",
                                                                                        'property_constraint_ID': property_constraint_ID if property_constraint_ID else "",
                                                                                        'property_constraint_unit': property_constraint_unit if property_constraint_unit else "",
                                                                                        'property_constraint_value': property_constraint_value if property_constraint_value else ""
                                                                                    }

                                                                                    # Only append if there are relevant information
                                                                                    if any(v != "" for v in constraint.values()):
                                                                                        prop_entry['property_constraint'].append(constraint)

                                            capability['properties'].append(prop_entry)

                                        property_type_submodelElementList = property_container.find("aas:value/aas:submodelElementList", ns)
                                        if property_type_submodelElementList is not None:

                                            prop_name = property_type_submodelElementList.find("aas:idShort", ns)
                                            prop_id = property_type_submodelElementList.find("aas:supplementalSemanticIds//aas:value", ns)
                                            unit = property_type_submodelElementList.find("aas:embeddedDataSpecifications//aas:value", ns)
                                            vtype = property_type_submodelElementList.find("aas:valueTypeListElement", ns)
                                            prop_relBy = property_container.find("aas:value/aas:relationshipElement/aas:second//aas:value", ns)

                                            result = {
                                                'property_name': prop_name.text if prop_name is not None else "",
                                                'property_comment': "<VAR>",
                                                'property_ID': prop_id.text if prop_id is not None else "",
                                                'property_unit': unit.text if unit is not None else "",
                                                'valueType': vtype.text if vtype is not None else ""
                                            }

                                            value_list = property_type_submodelElementList.findall("aas:value/aas:property", ns)
                                            for i, val_elem in enumerate(value_list):
                                                val = val_elem.find("aas:value", ns)
                                                result[f"value{i}"] = val.text if val is not None else ""

                                            result['property_realized_by'] = prop_relBy.text if prop_relBy is not None else ""

                                            capability['properties'].append(result)

                            # CapabilityRelations
                            for capability_relations in capability_container.findall(".//aas:submodelElementCollection", ns):
                                # Check if it's the CapabilityRelations block
                                capability_relations_semantic_id = capability_relations.find("aas:semanticId//aas:value", ns)
                                if capability_relations_semantic_id is not None and "https://admin-shell.io/idta/CapabilityDescription/CapabilityRelations/1/0" in capability_relations_semantic_id.text:

                                    for generalized_by_sets in capability_relations.findall("aas:value/aas:submodelElementCollection", ns):
                                        generalized_by_semantic_id = generalized_by_sets.find("aas:semanticId//aas:value", ns)
                                        if generalized_by_semantic_id is not None and "https://admin-shell.io/idta/CapabilityDescription/GeneralizedBySet/1/0" in generalized_by_semantic_id.text:

                                            for relationship_generalized_by in generalized_by_sets.findall("aas:value/aas:relationshipElement", ns):
                                                second_keys = relationship_generalized_by.find("aas:second/aas:keys", ns)
                                                if second_keys is not None:
                                                    key_elements = second_keys.findall("aas:key", ns)
                                                    if key_elements:
                                                        last_key = key_elements[-1]
                                                        last_value = last_key.find("aas:value", ns)
                                                        if last_value is not None:
                                                            capability['generalized_by'].append(last_value.text)

                                    for realized_by in capability_relations.findall("aas:value/aas:relationshipElement", ns):
                                        realized_by_semantic_id = realized_by.find("aas:semanticId//aas:value", ns)
                                        if realized_by_semantic_id is not None and "https://admin-shell.io/idta/CapabilityDescription/CapabilityRealizedBy/1/0" in realized_by_semantic_id.text:
                                            realized_by_value = realized_by.find("aas:second//aas:value", ns)
                                            if realized_by_value is not None:
                                                capability['realized_by'].append(realized_by_value.text)

                            capabilities.append(capability)

    return capabilities

def generate_random_values(capabilities):
    """Generate random values for capability properties (±20% range)"""
    random_capabilities = []
    
    for capability in capabilities:
        random_capability = capability.copy()
        random_capability['properties'] = []
        
        for prop in capability['properties']:
            random_prop = prop.copy()
            
            # Process properties with valueMin and valueMax
            if 'valueMin' in prop and 'valueMax' in prop and prop['valueMin'] and prop['valueMax']:
                try:
                    min_val = float(prop['valueMin'])
                    max_val = float(prop['valueMax'])
                    
                    # Calculate base value (midpoint)
                    base_value = (min_val + max_val) / 2
                    
                    # Generate random value within ±20% range
                    random_min = max(min_val, base_value * 0.8)
                    random_max = min(max_val, base_value * 1.2)
                    
                    random_value = random.uniform(random_min, random_max)
                    
                    # Format based on data type
                    if prop.get('valueType') == 'xs:int':
                        random_value = int(round(random_value))
                    else:
                        random_value = round(random_value, 2)
                    
                    random_prop['random_value'] = random_value
                    
                except (ValueError, TypeError):
                    random_prop['random_value'] = "N/A"
            
            # Process properties with value0 and value1 (e.g., RevolutionsPerMinute)
            elif 'value0' in prop and 'value1' in prop and prop['value0'] and prop['value1']:
                try:
                    val0 = float(prop['value0'])
                    val1 = float(prop['value1'])
                    
                    # Calculate base value
                    base_value = (val0 + val1) / 2
                    
                    # Generate random value within ±20% range
                    random_min = max(val0, base_value * 0.8)
                    random_max = min(val1, base_value * 1.2)
                    
                    random_value = random.uniform(random_min, random_max)
                    
                    if prop.get('valueType') == 'xs:int':
                        random_value = int(round(random_value))
                    else:
                        random_value = round(random_value, 2)
                    
                    random_prop['random_value'] = random_value
                    
                except (ValueError, TypeError):
                    random_prop['random_value'] = "N/A"
            
            else:
                random_prop['random_value'] = "N/A"
            
            random_capability['properties'].append(random_prop)
        
        random_capabilities.append(random_capability)
    
    return random_capabilities

def display_capabilities(capabilities):
    """Display capability data in terminal"""
    print("=" * 80)
    print("HC10_AAS Capability Data (with Random Parameter Values)")
    print("=" * 80)
    
    for i, capability in enumerate(capabilities, 1):
        cap_info = capability['capability'][0]
        print(f"\n{i}. Capability Name: {cap_info['capability_name']}")
        print(f"   Capability ID: {cap_info['capability_ID']}")
        
        if capability['generalized_by']:
            print(f"   Generalized by: {', '.join(capability['generalized_by'])}")
        
        if capability['realized_by']:
            print(f"   Realized by: {', '.join(capability['realized_by'])}")
        
        if capability['properties']:
            print("   Properties:")
            for prop in capability['properties']:
                print(f"     - {prop['property_name']}:")
                print(f"       Type: {prop.get('valueType', 'N/A')}")
                
                if 'valueMin' in prop and prop['valueMin']:
                    print(f"       Min Value: {prop['valueMin']}")
                if 'valueMax' in prop and prop['valueMax']:
                    print(f"       Max Value: {prop['valueMax']}")
                if 'value0' in prop and prop['value0']:
                    print(f"       Value 0: {prop['value0']}")
                if 'value1' in prop and prop['value1']:
                    print(f"       Value 1: {prop['value1']}")
                
                print(f"       Unit: {prop.get('property_unit', 'N/A')}")
                print(f"       Random Value: {prop.get('random_value', 'N/A')}")
                
                if prop.get('property_constraint'):
                    print(f"       Constraints: {prop['property_constraint']}")
        
        print("-" * 60)

# Main program
try:
    # Parse HC10 capabilities
    print("Parsing HC10_AAS.xml file...")
    hc10_capabilities = parse_hc10_capabilities(file_path)
    
    # Generate random values
    print("Generating random parameter values (±20% range)...")
    hc10_with_random = generate_random_values(hc10_capabilities)
    
    # Display in terminal
    display_capabilities(hc10_with_random)
    
    # Create output data structure
    output_data = {
        "resource: HC10_AAS": hc10_with_random
    }
    

except FileNotFoundError:
    print(f"Error: File not found {file_path}")
    print("Please ensure the file path is correct")
except ET.ParseError as e:
    print(f"XML parsing error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")