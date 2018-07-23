# Devops Framework

## Source Control

All code and configuration is stored in Github repos. 

Separate configuration is held at the account and product levels, with the 
configuration CMDB for each split across two physical repos - config and infrastructure.
There is a separate product CMDB for development and production environments.

All application settings, solution definitions and application deployment templates 
are stored in the config repo. All credentials and release templates are stored in the 
infrastructure repos. The distribution across two repos permits the allocation of different teams 
as contributors and maintainers, providing the granularity required for fine control
at different stages of the overall deployment process.

## Template Generation

As far as possible, all deployment activity wihin product accounts is achieved via
Cloud Formation. This largely negates the need for operational access to product accounts
for deployment activities.

Template generation is driven from the contents of the product CMDB config. The templates
take into account the configured availability requirements of each product environment, with
preproduction environments and above being set up for high availability.

The templates also completely define the infrastructure security model for products, since
all AWS resource access is performed by roles created as part of the cloud formation templates.

## Automation

The triggering of code builds, and the management of dpeloyment activities is standardised
in a series of Jenkins jobs. Authentication to the Jenkins server uses Github OAuth,
with Github teams being used to define permissions on jobs. Thus no authentication 
or authorisation information is held on the Jenkins server itself.

Code builds result in code "images", with an image built once and reused across all environments.
Images are stored in registries, which permit the atachment of tags to images in support
of the deployment processes. For docker images, the AWS ECR service is used, while other
formats are managed within an S3 bucket.

## Deployment Process

The deployment processes used permits the use of continual deployment for the integration environment,
and manual release processes for higher environments.

As a result, the development team obtain the benefit of rapid feedback on code commit within the Integration
environment, 
while deployment for higher environments dovetails with existing release management processes.

While manually triggered, the preparation and deployment of releases in higher environments
is highly scripted via Jenkins jobs, and requires no knowledge of the underlying processes
for their execution. In addition, acceptance and promotion steps are built into the process,
with the activity captured for audit processes within the product CMDB.
