# Copyright (c) 2011 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

{
  'target_defaults': {
    'variables': {
      'chrome_exe_target': 0,
    },
    'target_conditions': [
      ['chrome_exe_target==1', {
        'sources': [
          # .cc, .h, and .mm files under app that are used on all
          # platforms, including both 32-bit and 64-bit Windows.
          # Test files are not included.
          'app/breakpad_win.cc',
          'app/breakpad_win.h',
          'app/chrome_exe_main_gtk.cc',
          'app/chrome_exe_main_mac.mm',
          'app/chrome_exe_main_win.cc',
          'app/chrome_exe_resource.h',
          'app/client_util.cc',
          'app/client_util.h',
          'app/hard_error_handler_win.cc',
          'app/hard_error_handler_win.h',
          'app/scoped_ole_initializer.h',
          # TODO(bradnelson): once automatic generation of 64 bit targets on
          # Windows is ready, take this out and add a dependency on
          # content_common.gypi.
          '../content/common/content_switches.cc',
          '../content/common/content_switches.h',
        ],
        'mac_bundle_resources': [
          'app/app-Info.plist',
        ],
        # TODO(mark): Come up with a fancier way to do this.  It should only
        # be necessary to list app-Info.plist once, not the three times it is
        # listed here.
        'mac_bundle_resources!': [
          'app/app-Info.plist',
        ],
        'xcode_settings': {
          'CHROMIUM_STRIP_SAVE_FILE': 'app/app.saves',
          'INFOPLIST_FILE': 'app/app-Info.plist',
        },
        'conditions': [
          ['OS=="win"', {
            'msvs_settings': {
              'VCLinkerTool': {
                'DelayLoadDLLs': [
                  'dbghelp.dll',
                  'dwmapi.dll',
                  'uxtheme.dll',
                  'ole32.dll',
                  'oleaut32.dll',
                ],
                # Set /SUBSYSTEM:WINDOWS for chrome.exe itself.
                'SubSystem': '2',
              },
              'VCManifestTool': {
                'AdditionalManifestFiles': '$(ProjectDir)\\app\\chrome.exe.manifest',
              },
            },
            'actions': [
              {
                'action_name': 'first_run',
                'inputs': [
                    'app/FirstRun',
                ],
                'outputs': [
                    '<(PRODUCT_DIR)/First Run',
                ],
                'action': ['cp', '-f', '<@(_inputs)', '<@(_outputs)'],
                'message': 'Copy first run complete sentinel file',
              },
            ],
          }, {  # 'OS!="win"
            'sources!': [
              'app/client_util.cc',
            ]
          }],
        ],
      }],
    ],
  },
  'targets': [
    {
      'target_name': 'chrome',
      'type': 'executable',
      'mac_bundle': 1,
      'variables': {
        'chrome_exe_target': 1,
        'use_system_xdg_utils%': 0,
        'disable_pie%': 0,
      },
      'conditions': [
        ['os_posix == 1 and OS != "mac"', {
          'actions': [
            {
              'action_name': 'manpage',
              'conditions': [
                [ 'branding == "Chrome"', {
                  'variables': {
                    'name': 'Google Chrome',
                    'filename': 'google-chrome',
                    'confdir': 'google-chrome',
                  },
                }, { # else branding!="Chrome"
                  'variables': {
                    'name': 'Chromium',
                    'filename': 'chromium-browser',
                    'confdir': 'chromium',
                  },
                }],
              ],
              'inputs': [
                'tools/build/linux/sed.sh',
                'app/resources/manpage.1.in',
              ],
              'outputs': [
                '<(PRODUCT_DIR)/chrome.1',
              ],
              'action': [
                'tools/build/linux/sed.sh',
                'app/resources/manpage.1.in',
                '<@(_outputs)',
                '-e', 's/@@NAME@@/<(name)/',
                '-e', 's/@@FILENAME@@/<(filename)/',
                '-e', 's/@@CONFDIR@@/<(confdir)/',
              ],
              'message': 'Generating manpage'
            },
          ],
          'conditions': [
            ['linux_use_tcmalloc==1', {
                'dependencies': [
                  '<(allocator_target)',
                ],
              },
            ],
            # TODO(rkc): Remove disable_pie (and instead always use
            # -pie) once we have a fix for remote gdb and are able to
            # correctly get section header offsets for pie
            # executables. Currently -pie breaks remote debugging.
            ['disable_pie==1', {
              'ldflags': ['-nopie'],
            }, {
              # Building with -pie needs investigating on ARM.
              # For now, at least use it on Linux Intel.
              'conditions': [
                ['target_arch=="x64" or target_arch=="ia32"', {
                  'ldflags': ['-pie'],
                }],
              ],
            }],
            ['use_system_xdg_utils==0', {
              'copies': [
                {
                  'destination': '<(PRODUCT_DIR)',
                  'files': ['tools/build/linux/chrome-wrapper',
                            '../third_party/xdg-utils/scripts/xdg-mime',
                            '../third_party/xdg-utils/scripts/xdg-settings',
                            ],
                  # The wrapper script above may need to generate a .desktop
                  # file, which requires an icon. So, copy one next to the
                  # script.
                  'conditions': [
                    ['branding=="Chrome"', {
                      'files': ['app/theme/google_chrome/product_logo_48.png']
                    }, { # else: 'branding!="Chrome"
                      'files': ['app/theme/chromium/product_logo_48.png']
                    }],
                  ],
                },
              ],
            }],
          ],
          'dependencies': [
            # On Linux, link the dependencies (libraries) that make up actual
            # Chromium functionality directly into the executable.
            '<@(chromium_dependencies)',
            # Needed for chrome_main.cc initialization of libraries.
            '../build/linux/system.gyp:dbus-glib',
            '../build/linux/system.gyp:gtk',
            'packed_resources',
            # Needed to use the master_preferences functions
            'installer_util',
          ],
          'sources': [
            'app/chrome_dll_resource.h',
            'app/chrome_main.cc',
            'app/chrome_main_posix.cc',
          ],
        }],
        ['OS=="mac"', {
          # 'branding' is a variable defined in common.gypi
          # (e.g. "Chromium", "Chrome")
          'conditions': [
            ['branding=="Chrome"', {
              'mac_bundle_resources': [
                'app/theme/google_chrome/app.icns',
                'app/theme/google_chrome/document.icns',
                'browser/ui/cocoa/applescript/scripting.sdef',
              ],
            }, {  # else: 'branding!="Chrome"
              'mac_bundle_resources': [
                'app/theme/chromium/app.icns',
                'app/theme/chromium/document.icns',
                'browser/ui/cocoa/applescript/scripting.sdef',
              ],
            }],
            ['mac_breakpad==1', {
              'variables': {
                # A real .dSYM is needed for dump_syms to operate on.
                'mac_real_dsym': 1,
              },
              'xcode_settings': {
                # With mac_real_dsym set, strip_from_xcode won't be used.
                # Specify CHROMIUM_STRIP_SAVE_FILE directly to Xcode.
                'STRIPFLAGS': '-s $(CHROMIUM_STRIP_SAVE_FILE)',
              },
              'dependencies': [
                '../breakpad/breakpad.gyp:dump_syms',
                '../breakpad/breakpad.gyp:symupload',

                # In order to process symbols for the Remoting Host plugin,
                # that plugin needs to be built beforehand.  Since the
                # "Dump Symbols" step hangs off this target, that plugin also
                # needs to be added as a dependency.
                '../remoting/remoting.gyp:remoting_host_plugin',
              ],
              # The "Dump Symbols" post-build step is in a target_conditions
              # block so that it will follow the "Strip If Needed" step if that
              # is also being used.  There is no standard configuration where
              # both of these steps occur together, but Mark likes to use this
              # configuration sometimes when testing Breakpad-enabled builds
              # without the time overhead of creating real .dSYM files.  When
              # both "Dump Symbols" and "Strip If Needed" are present, "Dump
              # Symbols" must come second because "Strip If Needed" creates
              # a fake .dSYM that dump_syms needs to fake dump.  Since
              # "Strip If Needed" is added in a target_conditions block in
              # common.gypi, "Dump Symbols" needs to be in an (always true)
              # target_conditions block.
              'target_conditions': [
                ['1 == 1', {
                  'postbuilds': [
                    {
                      'postbuild_name': 'Dump Symbols',
                      'variables': {
                        'dump_product_syms_path':
                            'tools/build/mac/dump_product_syms',
                      },
                      'action': ['<(dump_product_syms_path)',
                                 '<(branding)'],
                    },
                  ],
                }],
              ],
            }],  # mac_breakpad
          ],
          'product_name': '<(mac_product_name)',
          'xcode_settings': {
            # chrome/app/app-Info.plist has:
            #   CFBundleIdentifier of CHROMIUM_BUNDLE_ID
            #   CFBundleName of CHROMIUM_SHORT_NAME
            #   CFBundleSignature of CHROMIUM_CREATOR
            # Xcode then replaces these values with the branded values we set
            # as settings on the target.
            'CHROMIUM_BUNDLE_ID': '<(mac_bundle_id)',
            'CHROMIUM_CREATOR': '<(mac_creator)',
            'CHROMIUM_SHORT_NAME': '<(branding)',
          },
          'dependencies': [
            'helper_app',
            'infoplist_strings_tool',
            'chrome_manifest_bundle',
          ],
          'mac_bundle_resources': [
            '<(PRODUCT_DIR)/<(mac_bundle_id).manifest',
          ],
          'actions': [
            {
              # Generate the InfoPlist.strings file
              'action_name': 'Generate InfoPlist.strings files',
              'variables': {
                'tool_path': '<(PRODUCT_DIR)/infoplist_strings_tool',
                # Unique dir to write to so the [lang].lproj/InfoPlist.strings
                # for the main app and the helper app don't name collide.
                'output_path': '<(INTERMEDIATE_DIR)/app_infoplist_strings',
              },
              'conditions': [
                [ 'branding == "Chrome"', {
                  'variables': {
                     'branding_name': 'google_chrome_strings',
                  },
                }, { # else branding!="Chrome"
                  'variables': {
                     'branding_name': 'chromium_strings',
                  },
                }],
              ],
              'inputs': [
                '<(tool_path)',
                '<(version_path)',
                # TODO: remove this helper when we have loops in GYP
                '>!@(<(apply_locales_cmd) \'<(grit_out_dir)/<(branding_name)_ZZLOCALE.pak\' <(locales))',
              ],
              'outputs': [
                # TODO: remove this helper when we have loops in GYP
                '>!@(<(apply_locales_cmd) -d \'<(output_path)/ZZLOCALE.lproj/InfoPlist.strings\' <(locales))',
              ],
              'action': [
                '<(tool_path)',
                '-b', '<(branding_name)',
                '-v', '<(version_path)',
                '-g', '<(grit_out_dir)',
                '-o', '<(output_path)',
                '-t', 'main',
                '<@(locales)',
              ],
              'message': 'Generating the language InfoPlist.strings files',
              'process_outputs_as_mac_bundle_resources': 1,
            },
          ],
          'copies': [
            {
              'destination': '<(PRODUCT_DIR)/<(mac_product_name).app/Contents/Versions/<(version_full)',
              'files': [
                '<(PRODUCT_DIR)/<(mac_product_name) Helper.app',
              ],
            },
          ],
          'postbuilds': [
            {
              'postbuild_name': 'Copy <(mac_product_name) Framework.framework',
              'action': [
                'tools/build/mac/copy_framework_unversioned',
                '${BUILT_PRODUCTS_DIR}/<(mac_product_name) Framework.framework',
                '${BUILT_PRODUCTS_DIR}/${CONTENTS_FOLDER_PATH}/Versions/<(version_full)',
              ],
            },
            {
              # Modify the Info.plist as needed.  The script explains why this
              # is needed.  This is also done in the helper_app and chrome_dll
              # targets.  Use -b0 to not include any Breakpad information; that
              # all goes into the framework's Info.plist.  Keystone information
              # is included if Keystone is enabled.  The application reads
              # Keystone keys from this plist and not the framework's, and
              # the ticket will reference this Info.plist to determine the tag
              # of the installed product.  Use -s1 to include Subversion
              # information.  The -p flag controls whether to insert PDF as a
              # supported type identifier that can be opened.
              'postbuild_name': 'Tweak Info.plist',
              'action': ['<(tweak_info_plist_path)',
                         '-b0',
                         '-k<(mac_keystone)',
                         '-s1',
                         '-p<(internal_pdf)',
                         '<(branding)',
                         '<(mac_bundle_id)'],
            },
            {
              'postbuild_name': 'Clean up old versions',
              'action': [
                'tools/build/mac/clean_up_old_versions',
                '<(version_full)'
              ],
            },
          ],  # postbuilds
        }],
        ['OS=="linux"', {
          'conditions': [
            ['branding=="Chrome"', {
              'dependencies': [
                'linux_installer_configs',
              ],
            }],
            ['selinux==0', {
              'dependencies': [
                '../sandbox/sandbox.gyp:sandbox',
              ],
            }],
          ],
        }],
        ['OS != "mac"', {
          'conditions': [
            # TODO:  add a:
            #   'product_name': 'chromium'
            # whenever we convert the rest of the infrastructure
            # (buildbots etc.) to understand the branding gyp define.
            # NOTE: chrome/app/theme/chromium/BRANDING and
            # chrome/app/theme/google_chrome/BRANDING have the short name
            # "chrome" etc.; should we try to extract from there instead?

            # On Mac, this is done in chrome_dll.gypi.
            ['internal_pdf', {
              'dependencies': [
                '../pdf/pdf.gyp:pdf',
              ],
            }],
          ],
          'dependencies': [
            'packed_extra_resources',
            # Copy Flash Player files to PRODUCT_DIR if applicable. Let the .gyp
            # file decide what to do on a per-OS basis; on Mac, internal plugins
            # go inside the framework, so this dependency is in chrome_dll.gypi.
            '../third_party/adobe/flash/flash_player.gyp:flash_player',
          ],
        }],
        ['OS=="mac"', {
          'dependencies': [
            # On Mac, make sure we've built chrome_dll, which contains all of
            # the library code with Chromium functionality.
            'chrome_dll',
          ],
        }],
        ['OS=="win"', {
          'conditions': [
            ['optimize_with_syzygy==1', {
              # With syzygy enabled there is an intermediate target which
              # builds an initial version of chrome_dll, then optimizes it
              # to its final location.  The optimization step also
              # depends on chrome_exe, so here we depend on the initial
              # chrome_dll.
              'dependencies': ['chrome_dll_initial',]
            }, {
              'dependencies': ['chrome_dll',]
            }],
          ],
        }],
        ['OS=="win"', {
          'dependencies': [
            'chrome_version_resources',
            'installer_util',
            'installer_util_strings',
            'packed_resources',
            '../base/base.gyp:base',
            '../breakpad/breakpad.gyp:breakpad_handler',
            '../breakpad/breakpad.gyp:breakpad_sender',
            '../sandbox/sandbox.gyp:sandbox',
            'app/policy/cloud_policy_codegen.gyp:policy',
          ],
          'sources': [
            'app/chrome_exe.rc',
            '<(SHARED_INTERMEDIATE_DIR)/chrome_version/chrome_exe_version.rc',
          ],
          'msvs_settings': {
            'VCLinkerTool': {
              'ImportLibrary': '$(OutDir)\\lib\\chrome_exe.lib',
              'ProgramDatabaseFile': '$(OutDir)\\chrome_exe.pdb',
            },
          },
        }],
      ],
    },
  ],
  'conditions': [
    ['OS=="win"', {
      'targets': [
        {
          'target_name': 'chrome_nacl_win64',
          'type': 'executable',
          'product_name': 'nacl64',
          'variables': {
            'chrome_exe_target': 1,
          },
          'dependencies': [
            # On Windows make sure we've built Win64 version of chrome_dll,
            # which contains all of the library code with Chromium
            # functionality.
            'chrome_version_resources',
            'chrome_dll_nacl_win64',
            'common_constants_win64',
            'installer_util_nacl_win64',
            'app/policy/cloud_policy_codegen.gyp:policy_win64',
            '../breakpad/breakpad.gyp:breakpad_handler_win64',
            '../breakpad/breakpad.gyp:breakpad_sender_win64',
            '../base/base.gyp:base_nacl_win64',
            '../base/base.gyp:base_static_win64',
            '../sandbox/sandbox.gyp:sandbox_win64',
          ],
          'defines': [
            '<@(nacl_win64_defines)',
          ],
          'include_dirs': [
            '<(SHARED_INTERMEDIATE_DIR)/chrome',
          ],
          'sources': [
            '<(SHARED_INTERMEDIATE_DIR)/chrome_version/nacl64_exe_version.rc',
          ],
          'msvs_settings': {
            'VCLinkerTool': {
              'ImportLibrary': '$(OutDir)\\lib\\nacl64_exe.lib',
              'ProgramDatabaseFile': '$(OutDir)\\nacl64_exe.pdb',
            },
          },
          'configurations': {
            'Common_Base': {
              'msvs_target_platform': 'x64',
            },
          },
        },
      ],
    }],
  ],
}
