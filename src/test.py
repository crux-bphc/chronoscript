import create_json
import pandas as pd
import json, numpy as np




def format(obj : dict) -> dict:
    """
    Function to convert 'instructor' list to set.Required because assert function checks 
    for equality which lead to test failure in case of list with different order of elements, for example let
    
    list1 = ['Instructor 2', 'Instructor 1']
    list2 = ['Instructor 1', 'Instructor 2']

    list1 and list2 are not equal but for sets order is unimportant.

    Args:
        obj(dict): The dictionary with list of instructors.
        
    Returns:
        dict: The converted dictionary with set of instructors.
    """
    for data in obj.values(): 
        for section in data['sections'].values():
            section['instructor'] = set(section['instructor'])


def test(obj : list[list[str]], expected_output: dict,output_file) -> str:
        data = pd.DataFrame(obj)
        create_json.create_json_file(data,columns,output_file)
        output_data = json.loads(open(output_file, "r").read())
        format(output_data)
        assert output_data == expected_output, "Conversion failed!"
        return "TEST PASS"


csv_data_1 = [
    ["1111","COU-1","Course-1","3","","3","1","Instructor 1","G101","T Th S","4","13/03 9.30 - 11.00AM","08/05 FN",]
]


expected_output_1 = {
    "COU-1": {
        "course_name": "Course-1",
        "sections": {
            "L1": {
                "instructor": {"Instructor 1"},
                "schedule": [{"room": "G101", "days": ["T", "Th", "S"], "hours": [4]}],
            }
        },
        "exams": [{"midsem": "13/03 9.30 - 11.00AM", "compre": "08/05 FN"}],
    }
}




csv_data_2 = [
    ["2222","COU-2","Course-2","3","-","3","1","Instructor 1","G102","M W F","9","16/03 4.00 - 5.30PM","16/05 AN"],
    [np.NaN,np.NaN,np.NaN,np.NaN,np.NaN,np.NaN,np.NaN,"Instructor 2",np.NaN,np.NaN,np.NaN,np.NaN,np.NaN,],
]


expected_output_2 = {
    "COU-2": {
        "course_name": "Course-2",
        "sections": {
            "L1": {"instructor": {"Instructor 1","Instructor 2"},
                "schedule": [{"room": "G102","days": ["M","W","F"],"hours": [9]}]
            }
        },
        "exams": [{"midsem": "16/03 4.00 - 5.30PM","compre": "16/05 AN"}]
    }
}




csv_data_3 = [
    ['3333', 'COU-3', 'Course-3', '3', '-', '3', '1', 'Instructor 1', 'G103', 'M W F', '3', '14/03 9.30 - 11.00AM', '10/05 FN '],
    [np.NaN,np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, 'Instructor 2', np.NaN, np.NaN, np.NaN, np.NaN, np.NaN],
    [np.NaN, np.NaN, "Tutorial", np.NaN, np.NaN, np.NaN, np.NaN, "T_instructor 1", "G103", "S", "1", np.NaN, np.NaN],
    [np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, "T_instructor 2", np.NaN, np.NaN, np.NaN, np.NaN, np.NaN],
]


expected_output_3 = {
    "COU-3": {
        "course_name": "Course-3",
        "sections": {
            "L1": {"instructor": {"Instructor 1","Instructor 2"},
                                "schedule": [{"room": "G103","days": ["M","W","F"],"hours": [3]}]
                                },
                "T1": {"instructor": {"T_instructor 1","T_instructor 2"},
                                "schedule": [{"room": "G103","days": ["S"],"hours": [1]}]
                                }
},
        "exams": [{"midsem": "14/03 9.30 - 11.00AM","compre": "10/05 FN "}]
    }}




csv_data_4 = [
    ['4444', 'COU-4', 'Course-4', '3', '1', '4', '1', 'instructor 1', 'F102', 'M W F', '3', '14/03 9.30 - 11.00AM', '10/05 FN',],
    [np.NaN, np.NaN, 'Practical', np.NaN, np.NaN, np.NaN, '1', 'P_instructor 1', 'D313', 'M', '6 7', np.NaN, np.NaN],
    [np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, "P_instructor 2", np.NaN, np.NaN, np.NaN, np.NaN, np.NaN],
    [np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, "2", "P_instructor 3", "D313", "W", "6 7", np.NaN, np.NaN],
    [np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, "P_instructor 4", np.NaN, np.NaN, np.NaN, np.NaN, np.NaN],
    [np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, "3", "P_instructor 5", "D313", "T", "2 3", np.NaN, np.NaN],
    [np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, "P_instructor 6", np.NaN, np.NaN, np.NaN, np.NaN, np.NaN],
    [np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, "4", "P_instructor 7", "D313", "Th", "2 3", np.NaN, np.NaN],
    [np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, "P_instructor 8", np.NaN, np.NaN, np.NaN, np.NaN, np.NaN],
    [np.NaN, np.NaN, "Tutorial", np.NaN, np.NaN, np.NaN, 1, "T_instructor 1", "G103", "S", "1", np.NaN, np.NaN],
    [np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, "T_instructor 2", np.NaN, np.NaN, np.NaN, np.NaN, np.NaN],
    [np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, 2, "T_instructor 3", "G105", "S", "1", np.NaN, np.NaN],
    [np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, np.NaN, "T_instructor 4", np.NaN, np.NaN, np.NaN, np.NaN, np.NaN]
    ]


expected_output_4 = {
    "COU-4": {
        "course_name": "Course-4",
        "sections": {
            "L1": {"instructor": {"instructor 1"},
                                "schedule": [{"room": "F102","days": ["M","W","F"],"hours": [3]}]
                    },
                        "P1": {"instructor": {"P_instructor 2","P_instructor 1"},
                                "schedule": [{"room": "D313","days": ["M"],"hours": [6,7]}]
                                },
                        "P2": {"instructor": {"P_instructor 4","P_instructor 3"},
                                "schedule": [{"room": "D313","days": ["W"],"hours": [6,7]}]
                                },
                        "P3": {"instructor": {"P_instructor 6","P_instructor 5"},
                                "schedule": [{"room": "D313","days": ["T"],"hours": [2,3]}]
                                },
                        "P4": {"instructor": {"P_instructor 8","P_instructor 7"},
                                "schedule": [{"room": "D313","days": ["Th"],"hours": [2,3]}]
                                },
                        "T1": {"instructor": {"T_instructor 2","T_instructor 1"},
                                "schedule": [{"room": "G103","days": ["S"],"hours": [1]}]
                                },
                        "T2": {"instructor": {"T_instructor 3","T_instructor 4"},
                                "schedule": [{"room": "G105","days": ["S"],"hours": [1]}]
                                }
                                },
"exams": [{"midsem": "14/03 9.30 - 11.00AM","compre": "10/05 FN"}]
    }
}




columns = [
    "serial",
    "course_code",
    "course_name",
    "L",
    "P",
    "U",
    "section",
    "instructor",
    "room",
    "days",
    "hours",
    "midsem",
    "compre",
]




if __name__ == "__main__":
    for i in range(100000):
        test(csv_data_1,expected_output_1,"test_out_1")
        test(csv_data_2,expected_output_2,"test_out_2")
        test(csv_data_3,expected_output_3,"test_out_3")
        test(csv_data_4,expected_output_4,"test_out_4")
