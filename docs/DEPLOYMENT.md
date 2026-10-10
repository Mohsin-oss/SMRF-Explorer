# Source hosting and website hosting

## Current private site

The working application is hosted at:

https://smrf-model-explorer.mr-hydrogen-bond.chatgpt.site/?v=3#project

Access is controlled by its current hosting service. Static source files do not implement authentication themselves. The GitHub distribution excludes host-specific project IDs, source-repository configuration, credentials and Git history. Updating this repository does not automatically update the hosted Site.

## GitHub repository

Repository: [Mohsin-oss/SMRF-Explorer](https://github.com/Mohsin-oss/SMRF-Explorer), visibility **Private**.

The CI workflow validates the source and downloadable runner on pushes and pull requests. It has read-only repository permissions and no publishing step. A repository upload is source hosting, not a website deployment.

If creating the repository manually, select Private and initialize it with a README so the default branch has a commit. If the GitHub app is restricted to selected repositories, grant it access to the new repository. The prepared README will replace that initial placeholder.

## GitHub Pages

GitHub Pages sites are public by default, even when built from a private repository. Private Pages access control is available for eligible organization project sites using GitHub Enterprise Cloud. Do not enable Pages for this personal repository while private hosting is required.

Official guidance: [Creating a GitHub Pages site](https://docs.github.com/en/enterprise-cloud@latest/pages/getting-started-with-github-pages/creating-a-github-pages-site) and [changing site visibility](https://docs.github.com/en/enterprise-cloud@latest/pages/getting-started-with-github-pages/changing-the-visibility-of-your-github-pages-site).

## Other viable paths

- Keep the existing private host and maintain source/version history in the private GitHub repository.
- Use another static host with verified authentication, publishing `dist/` as the site root.
- Use eligible private GitHub Pages under an Enterprise Cloud organization.
- If the owner later approves public publication, configure a separate public deployment workflow after reviewing code, assets and data. No such workflow is included now.

No hosting access tokens are required to run local checks. Never commit hosting credentials, user model files or processing results.
