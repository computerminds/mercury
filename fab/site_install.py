from pantheon import install
from pantheon import status
from pantheon import logger

#TODO: Move logging into pantheon libraries for better coverage.
def install_site(project='pantheon', profile='pantheon', version=6, **kw):
    """ Create a new Drupal installation.
    project: Installation namespace.
    profile: The installation type (e.g. pantheon/openatrium)
    version: Major drupal version.

    """
    data = {'profile': profile,
            'project': project,
            'version': version}

    log = logger.logging.getLogger('pantheon.install.site')
    log = logger.logging.LoggerAdapter(log, data)
    log.info('Site installation of %s using %s version %s initiated.' % 
             (project, profile, version))
    try:
        handler = _get_profile_handler(**data)
        handler.build(**data)
    except:
        log.exception('Site installation was unsuccessful')
        raise
    else:
        log.info('Site installation successful')

class _PantheonProfile(install.InstallTools):
    """ Default Pantheon Installation Profile.

    """
    def build(self, **kw):

        # Remove existing project.
        self.remove_project()

        # Create a new project
        self.setup_project_repo()
        self.setup_project_branch()
        self.setup_working_dir()

        # Run bcfg2 project bundle.
        self.bcfg2_project()

        # Setup project
        self.setup_database()
        self.setup_files_dir()
        self.setup_settings_file()
        self.setup_pantheon_modules()
        self.setup_pantheon_libraries()

        # Push changes from working directory to central repo
        self.push_to_repo()

        # Build non-code site features.
        self.setup_solr_index()
        self.setup_drupal_cron()
        self.setup_drush_alias()

        # Clone project to all environments
        self.setup_environments()

        # Cleanup and restart services
        self.cleanup()
        self.server.restart_services()

        # Send back repo status.
        status.git_repo_status(self.project)
        status.drupal_update_status(self.project)

        # Set permissions on project
        self.setup_permissions()

"""
To define additional profile handlers:
   1. Create a new profile class
   2. Add profile name and class to profiles dict in _get_profiles_handler().
"""

def _get_profile_handler(profile, **kw):
    """ Return instantiated profile object.
        profile: name of the installation profile.

    """
    profiles = {'pantheon': _PantheonProfile}

    # If profile: doesn't exist, use 'pantheon'
    return profiles.has_key(profile) and \
           profiles[profile](**kw) or \
           profiles['pantheon'](**kw)

