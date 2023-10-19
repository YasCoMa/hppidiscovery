{
    "cwlVersion": "v1.0",
    "$graph": [
        {
            "class": "CommandLineTool",
            "id": "#snakemake-job",
            "label": "Snakemake job executor",
            "hints": [
                {
                    "dockerPull": "snakemake/snakemake:v7.18.1",
                    "class": "DockerRequirement"
                }
            ],
            "baseCommand": "snakemake",
            "requirements": {
                "ResourceRequirement": {
                    "coresMin": "$(inputs.cores)"
                }
            },
            "arguments": [
                "--force",
                "--keep-target-files",
                "--keep-remote",
                "--force-use-threads",
                "--wrapper-prefix",
                "https://github.com/snakemake/snakemake-wrappers/raw/",
                "--notemp",
                "--quiet",
                "--use-conda",
                "--no-hooks",
                "--nolock",
                "--mode",
                "1"
            ],
            "inputs": {
                "snakefile": {
                    "type": "File",
                    "default": {
                        "class": "File",
                        "location": "Snakefile"
                    },
                    "inputBinding": {
                        "prefix": "--snakefile"
                    }
                },
                "sources": {
                    "type": "File[]",
                    "default": [
                        {
                            "class": "File",
                            "location": "get_metrics.py"
                        },
                        {
                            "class": "File",
                            "location": "predprin"
                        },
                        {
                            "class": "File",
                            "location": "data_preprocessing.py"
                        },
                        {
                            "class": "File",
                            "location": "test_Snakefile"
                        },
                        {
                            "class": "File",
                            "location": "clean_steps.py"
                        },
                        {
                            "class": "File",
                            "location": "config_laptop.yaml"
                        },
                        {
                            "class": "File",
                            "location": "workflow.png"
                        },
                        {
                            "class": "File",
                            "location": "hp_ppi_augmentation.yml"
                        },
                        {
                            "class": "File",
                            "location": "Snakefile"
                        },
                        {
                            "class": "File",
                            "location": "params_example.tsv"
                        },
                        {
                            "class": "File",
                            "location": "params_augmentation.tsv"
                        },
                        {
                            "class": "File",
                            "location": "dag.pdf"
                        },
                        {
                            "class": "File",
                            "location": "clean_outputs.sh"
                        },
                        {
                            "class": "File",
                            "location": "training_ppi_augmentation.py"
                        },
                        {
                            "class": "File",
                            "location": "list_virulence_factors_full.tsv"
                        },
                        {
                            "class": "File",
                            "location": "taxdump.tar.gz"
                        },
                        {
                            "class": "File",
                            "location": "data_preprocessing_v1.py"
                        },
                        {
                            "class": "File",
                            "location": "mapping_geneName_uniprot.tsv"
                        },
                        {
                            "class": "File",
                            "location": "readme.md"
                        },
                        {
                            "class": "File",
                            "location": "evaluation_visualization.py"
                        },
                        {
                            "class": "File",
                            "location": "config.yaml"
                        },
                        {
                            "class": "File",
                            "location": "config_example.yaml"
                        },
                        {
                            "class": "File",
                            "location": "reduced_workflow.png"
                        }
                    ]
                },
                "cores": {
                    "type": "int",
                    "default": 1,
                    "inputBinding": {
                        "prefix": "--cores"
                    }
                },
                "rules": {
                    "type": "string[]?",
                    "inputBinding": {
                        "prefix": "--allowed-rules"
                    }
                },
                "input_files": {
                    "type": "File[]",
                    "default": []
                },
                "target_files": {
                    "type": "string[]?",
                    "inputBinding": {
                        "position": 0
                    }
                }
            },
            "outputs": {
                "output_files": {
                    "type": {
                        "type": "array",
                        "items": "File"
                    },
                    "outputBinding": {
                        "glob": "$(inputs.target_files)"
                    }
                }
            }
        },
        {
            "class": "Workflow",
            "requirements": {
                "InlineJavascriptRequirement": {},
                "MultipleInputFeatureRequirement": {}
            },
            "steps": [
                {
                    "run": "#snakemake-job",
                    "requirements": {
                        "InitialWorkDirRequirement": {
                            "listing": [
                                {
                                    "writable": true,
                                    "entry": "$({'class': 'Directory', 'basename': '..', 'listing': [{'class': 'Directory', 'basename': 'input_example', 'listing': [{'class': 'File', 'basename': 'ev_step5.txt', 'location': inputs.input_files[0].location}]}]})"
                                }
                            ]
                        }
                    },
                    "in": {
                        "cores": {
                            "default": 1
                        },
                        "target_files": {
                            "default": []
                        },
                        "rules": {
                            "default": [
                                "all"
                            ]
                        },
                        "input_files": {
                            "source": [
                                "#main/job-1/output_files"
                            ],
                            "linkMerge": "merge_flattened"
                        }
                    },
                    "out": [
                        "output_files"
                    ],
                    "id": "#main/job-0"
                },
                {
                    "run": "#snakemake-job",
                    "requirements": {
                        "InitialWorkDirRequirement": {
                            "listing": [
                                {
                                    "writable": true,
                                    "entry": "$({'class': 'Directory', 'basename': '..', 'listing': [{'class': 'Directory', 'basename': 'input_example', 'listing': [{'class': 'File', 'basename': 'ev_step4.txt', 'location': inputs.input_files[0].location}]}]})"
                                }
                            ]
                        }
                    },
                    "in": {
                        "cores": {
                            "default": 1
                        },
                        "target_files": {
                            "default": [
                                "../input_example/ev_step5.txt"
                            ]
                        },
                        "rules": {
                            "default": [
                                "evaluation_visualization_step5"
                            ]
                        },
                        "input_files": {
                            "source": [
                                "#main/job-2/output_files"
                            ],
                            "linkMerge": "merge_flattened"
                        }
                    },
                    "out": [
                        "output_files"
                    ],
                    "id": "#main/job-1"
                },
                {
                    "run": "#snakemake-job",
                    "requirements": {
                        "InitialWorkDirRequirement": {
                            "listing": [
                                {
                                    "writable": true,
                                    "entry": "$({'class': 'Directory', 'basename': '..', 'listing': [{'class': 'Directory', 'basename': 'input_example', 'listing': [{'class': 'File', 'basename': 'ev_step3.txt', 'location': inputs.input_files[0].location}]}]})"
                                }
                            ]
                        }
                    },
                    "in": {
                        "cores": {
                            "default": 1
                        },
                        "target_files": {
                            "default": [
                                "../input_example/ev_step4.txt"
                            ]
                        },
                        "rules": {
                            "default": [
                                "evaluation_visualization_step4"
                            ]
                        },
                        "input_files": {
                            "source": [
                                "#main/job-3/output_files"
                            ],
                            "linkMerge": "merge_flattened"
                        }
                    },
                    "out": [
                        "output_files"
                    ],
                    "id": "#main/job-2"
                },
                {
                    "run": "#snakemake-job",
                    "requirements": {
                        "InitialWorkDirRequirement": {
                            "listing": [
                                {
                                    "writable": true,
                                    "entry": "$({'class': 'Directory', 'basename': '..', 'listing': [{'class': 'Directory', 'basename': 'input_example', 'listing': [{'class': 'File', 'basename': 'ev_step2.txt', 'location': inputs.input_files[0].location}]}]})"
                                }
                            ]
                        }
                    },
                    "in": {
                        "cores": {
                            "default": 1
                        },
                        "target_files": {
                            "default": [
                                "../input_example/ev_step3.txt"
                            ]
                        },
                        "rules": {
                            "default": [
                                "evaluation_visualization_step3"
                            ]
                        },
                        "input_files": {
                            "source": [
                                "#main/job-4/output_files"
                            ],
                            "linkMerge": "merge_flattened"
                        }
                    },
                    "out": [
                        "output_files"
                    ],
                    "id": "#main/job-3"
                },
                {
                    "run": "#snakemake-job",
                    "requirements": {
                        "InitialWorkDirRequirement": {
                            "listing": [
                                {
                                    "writable": true,
                                    "entry": "$({'class': 'Directory', 'basename': '..', 'listing': [{'class': 'Directory', 'basename': 'input_example', 'listing': [{'class': 'File', 'basename': 'ev_step1.txt', 'location': inputs.input_files[0].location}]}]})"
                                }
                            ]
                        }
                    },
                    "in": {
                        "cores": {
                            "default": 1
                        },
                        "target_files": {
                            "default": [
                                "../input_example/ev_step2.txt"
                            ]
                        },
                        "rules": {
                            "default": [
                                "evaluation_visualization_step2"
                            ]
                        },
                        "input_files": {
                            "source": [
                                "#main/job-5/output_files"
                            ],
                            "linkMerge": "merge_flattened"
                        }
                    },
                    "out": [
                        "output_files"
                    ],
                    "id": "#main/job-4"
                },
                {
                    "run": "#snakemake-job",
                    "requirements": {
                        "InitialWorkDirRequirement": {
                            "listing": [
                                {
                                    "writable": true,
                                    "entry": "$({'class': 'Directory', 'basename': '..', 'listing': [{'class': 'Directory', 'basename': 'input_example', 'listing': [{'class': 'File', 'basename': 'tpa_step3.txt', 'location': inputs.input_files[0].location}]}]})"
                                }
                            ]
                        }
                    },
                    "in": {
                        "cores": {
                            "default": 1
                        },
                        "target_files": {
                            "default": [
                                "../input_example/ev_step1.txt"
                            ]
                        },
                        "rules": {
                            "default": [
                                "evaluation_visualization_step1"
                            ]
                        },
                        "input_files": {
                            "source": [
                                "#main/job-6/output_files"
                            ],
                            "linkMerge": "merge_flattened"
                        }
                    },
                    "out": [
                        "output_files"
                    ],
                    "id": "#main/job-5"
                },
                {
                    "run": "#snakemake-job",
                    "requirements": {
                        "InitialWorkDirRequirement": {
                            "listing": [
                                {
                                    "writable": true,
                                    "entry": "$({'class': 'Directory', 'basename': '..', 'listing': [{'class': 'Directory', 'basename': 'input_example', 'listing': [{'class': 'File', 'basename': 'tpa_step2.txt', 'location': inputs.input_files[0].location}]}]})"
                                }
                            ]
                        }
                    },
                    "in": {
                        "cores": {
                            "default": 1
                        },
                        "target_files": {
                            "default": [
                                "../input_example/tpa_step3.txt"
                            ]
                        },
                        "rules": {
                            "default": [
                                "training_ppi_augmentation_step3"
                            ]
                        },
                        "input_files": {
                            "source": [
                                "#main/job-7/output_files"
                            ],
                            "linkMerge": "merge_flattened"
                        }
                    },
                    "out": [
                        "output_files"
                    ],
                    "id": "#main/job-6"
                },
                {
                    "run": "#snakemake-job",
                    "requirements": {
                        "InitialWorkDirRequirement": {
                            "listing": [
                                {
                                    "writable": true,
                                    "entry": "$({'class': 'Directory', 'basename': '..', 'listing': [{'class': 'Directory', 'basename': 'input_example', 'listing': [{'class': 'File', 'basename': 'tpa_step1.txt', 'location': inputs.input_files[0].location}]}]})"
                                }
                            ]
                        }
                    },
                    "in": {
                        "cores": {
                            "default": 1
                        },
                        "target_files": {
                            "default": [
                                "../input_example/tpa_step2.txt"
                            ]
                        },
                        "rules": {
                            "default": [
                                "training_ppi_augmentation_step2"
                            ]
                        },
                        "input_files": {
                            "source": [
                                "#main/job-8/output_files"
                            ],
                            "linkMerge": "merge_flattened"
                        }
                    },
                    "out": [
                        "output_files"
                    ],
                    "id": "#main/job-7"
                },
                {
                    "run": "#snakemake-job",
                    "requirements": {
                        "InitialWorkDirRequirement": {
                            "listing": [
                                {
                                    "writable": true,
                                    "entry": "$({'class': 'Directory', 'basename': '..', 'listing': [{'class': 'Directory', 'basename': 'input_example', 'listing': [{'class': 'File', 'basename': 'da_step3.txt', 'location': inputs.input_files[0].location}]}]})"
                                }
                            ]
                        }
                    },
                    "in": {
                        "cores": {
                            "default": 1
                        },
                        "target_files": {
                            "default": [
                                "../input_example/tpa_step1.txt"
                            ]
                        },
                        "rules": {
                            "default": [
                                "training_ppi_augmentation_step1"
                            ]
                        },
                        "input_files": {
                            "source": [
                                "#main/job-9/output_files"
                            ],
                            "linkMerge": "merge_flattened"
                        }
                    },
                    "out": [
                        "output_files"
                    ],
                    "id": "#main/job-8"
                },
                {
                    "run": "#snakemake-job",
                    "requirements": {
                        "InitialWorkDirRequirement": {
                            "listing": [
                                {
                                    "writable": true,
                                    "entry": "$({'class': 'Directory', 'basename': '..', 'listing': [{'class': 'Directory', 'basename': 'input_example', 'listing': [{'class': 'File', 'basename': 'da_step2.txt', 'location': inputs.input_files[0].location}]}]})"
                                }
                            ]
                        }
                    },
                    "in": {
                        "cores": {
                            "default": 1
                        },
                        "target_files": {
                            "default": [
                                "../input_example/da_step3.txt"
                            ]
                        },
                        "rules": {
                            "default": [
                                "data_acquisition_step3"
                            ]
                        },
                        "input_files": {
                            "source": [
                                "#main/job-10/output_files"
                            ],
                            "linkMerge": "merge_flattened"
                        }
                    },
                    "out": [
                        "output_files"
                    ],
                    "id": "#main/job-9"
                },
                {
                    "run": "#snakemake-job",
                    "requirements": {
                        "InitialWorkDirRequirement": {
                            "listing": [
                                {
                                    "writable": true,
                                    "entry": "$({'class': 'Directory', 'basename': '..', 'listing': [{'class': 'Directory', 'basename': 'input_example', 'listing': [{'class': 'File', 'basename': 'da_step1.txt', 'location': inputs.input_files[0].location}]}]})"
                                }
                            ]
                        }
                    },
                    "in": {
                        "cores": {
                            "default": 1
                        },
                        "target_files": {
                            "default": [
                                "../input_example/da_step2.txt"
                            ]
                        },
                        "rules": {
                            "default": [
                                "data_acquisition_step2"
                            ]
                        },
                        "input_files": {
                            "source": [
                                "#main/job-11/output_files"
                            ],
                            "linkMerge": "merge_flattened"
                        }
                    },
                    "out": [
                        "output_files"
                    ],
                    "id": "#main/job-10"
                },
                {
                    "run": "#snakemake-job",
                    "requirements": {
                        "InitialWorkDirRequirement": {
                            "listing": []
                        }
                    },
                    "in": {
                        "cores": {
                            "default": 1
                        },
                        "target_files": {
                            "default": [
                                "../input_example/da_step1.txt"
                            ]
                        },
                        "rules": {
                            "default": [
                                "data_acquisition_step1"
                            ]
                        },
                        "input_files": {
                            "source": [],
                            "linkMerge": "merge_flattened"
                        }
                    },
                    "out": [
                        "output_files"
                    ],
                    "id": "#main/job-11"
                }
            ],
            "inputs": [],
            "outputs": [
                {
                    "type": {
                        "type": "array",
                        "items": "File"
                    },
                    "outputSource": "#main/job-0/output_files",
                    "id": "#main/output/job-0"
                }
            ],
            "id": "#main"
        }
    ]
}