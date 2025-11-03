# Feature Specification: Azure DevOps Specify Workflow Integration

**Feature Branch**: `005-ado-specify-integration`  
**Created**: 2025-11-03  
**Status**: Draft  
**Input**: User description: "I want the following changes to Specify workflow:
1. Once Spec Kit create a new branch for the feature, immediately link it to Azure DevOps feature with 'GitHub Branch' type of link in 'Development' tab
2. Once workflow created at least one Issue WI under Feature, put the Feature into 'Blocked' state and on top of the Blocked column, and assign to the user who triggered the workflow in Azure DevOps
3. When Specify workflow triggered and Feature has unclosed Issues underneath, then: 
If there is no spec.md file for the current feature, then pass Feature Description and all Issues' descriptions to the workflow
If there is spec.md file for the current feature, then pass all Issues' descriptions to the workflow
4. When Specify workflow triggered and Feature does not have Issues underneath or all underneath Issues are closed, then: 
Pass Feature Description to the workflow"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automatic Branch Linking to Azure DevOps (Priority: P1)

When a team member triggers the Specify workflow to create a new feature, the system automatically creates a GitHub branch and links it to the corresponding Azure DevOps Feature work item in the Development tab. This ensures traceability between the feature specification work and the Azure DevOps backlog without manual intervention.

**Why this priority**: This is the foundation for integration between GitHub and Azure DevOps, enabling automatic tracking of feature development. Without this, all subsequent workflow steps cannot provide proper visibility in Azure DevOps.

**Independent Test**: Can be fully tested by triggering the Specify workflow with a new feature and verifying that the Azure DevOps Feature work item contains a 'GitHub Branch' link in its Development tab pointing to the created branch.

**Acceptance Scenarios**:

1. **Given** a user has triggered the Specify workflow with a new feature description, **When** the workflow creates a new feature branch, **Then** the Azure DevOps Feature work item must have a 'GitHub Branch' type link added to its Development tab pointing to the new branch
2. **Given** the branch link is created in Azure DevOps, **When** a user views the Feature work item, **Then** the Development tab must show the GitHub branch link with the correct branch name
3. **Given** the Specify workflow fails to create the branch, **When** the error occurs, **Then** no link should be created in Azure DevOps and the user should receive an error notification

---

### User Story 2 - Automatic Feature Blocking and Assignment (Priority: P2)

When the Specify workflow creates Issue work items under a Feature in Azure DevOps, the system automatically moves the Feature to 'Blocked' state, positions it at the top of the Blocked column, and assigns it to the user who triggered the workflow. This ensures that features requiring clarification are immediately visible and owned by the right person.

**Why this priority**: This automates the workflow state management and ensures accountability. It's dependent on Issue creation (which follows specification generation) but is critical for workflow management and visibility.

**Independent Test**: Can be fully tested by triggering a Specify workflow that generates Issues, then verifying in Azure DevOps that the parent Feature is in 'Blocked' state, positioned at the top of the Blocked column, and assigned to the workflow initiator.

**Acceptance Scenarios**:

1. **Given** the Specify workflow has created at least one Issue work item under a Feature, **When** the Issue creation completes, **Then** the parent Feature work item must be moved to 'Blocked' state
2. **Given** a Feature is moved to 'Blocked' state, **When** the state change is applied, **Then** the Feature must appear at the top position of the Blocked column in Azure DevOps board view
3. **Given** a Feature is being blocked due to Issues, **When** the state change occurs, **Then** the Feature must be assigned to the user who triggered the Specify workflow
4. **Given** a Feature already has other work items in 'Blocked' state, **When** this Feature is blocked, **Then** it must be positioned above all other blocked items

---

### User Story 3 - Context-Aware Input Handling with Existing Issues (Priority: P3)

When a team member triggers the Specify workflow for a Feature that has unclosed Issues, the system intelligently determines what information to pass to the workflow based on whether a specification file already exists. If no spec.md exists, both the Feature Description and all unclosed Issue descriptions are provided. If spec.md exists, only the unclosed Issue descriptions are provided for refinement.

**Why this priority**: This enables iterative refinement of specifications based on clarification questions. It's a supporting feature for the workflow but doesn't block initial specification creation.

**Independent Test**: Can be fully tested by creating a Feature with unclosed Issues, triggering the Specify workflow, and verifying the workflow receives the correct input data based on the presence/absence of spec.md file.

**Acceptance Scenarios**:

1. **Given** a Feature has unclosed Issues and no spec.md file exists, **When** the Specify workflow is triggered, **Then** the workflow must receive both the Feature Description and all unclosed Issue descriptions as input
2. **Given** a Feature has unclosed Issues and a spec.md file exists, **When** the Specify workflow is triggered, **Then** the workflow must receive only the unclosed Issue descriptions as input (not the Feature Description)
3. **Given** a Feature has both closed and unclosed Issues, **When** the Specify workflow is triggered, **Then** only unclosed Issue descriptions must be included in the workflow input
4. **Given** a Feature has Issues but cannot determine if spec.md exists, **When** the Specify workflow is triggered, **Then** the system must treat it as if no spec.md exists and include both Feature Description and Issue descriptions

---

### User Story 4 - Clean Slate Input Handling (Priority: P3)

When a team member triggers the Specify workflow for a Feature that has no Issues or all Issues are closed, the system passes only the Feature Description to the workflow. This represents a clean specification generation or re-generation scenario.

**Why this priority**: This handles the standard case of initial specification creation or starting fresh after all clarifications are resolved. It's equally important as Story 3 but doesn't have dependencies.

**Independent Test**: Can be fully tested by creating a Feature with no Issues (or all closed Issues), triggering the Specify workflow, and verifying the workflow receives only the Feature Description as input.

**Acceptance Scenarios**:

1. **Given** a Feature has no Issue work items underneath it, **When** the Specify workflow is triggered, **Then** the workflow must receive only the Feature Description as input
2. **Given** a Feature has Issues but all are in closed state, **When** the Specify workflow is triggered, **Then** the workflow must receive only the Feature Description as input
3. **Given** a Feature has mixed closed and unclosed Issues, **When** all remaining Issues are closed and workflow is triggered, **Then** the workflow must receive only the Feature Description (reverting to clean slate mode)

---

### Edge Cases

- What happens when the Azure DevOps API is unavailable during branch link creation? System should retry with exponential backoff and notify the user if the link cannot be created after retries.
- How does the system handle concurrent Specify workflow executions for the same Feature? System should queue requests and process them sequentially to prevent race conditions.
- What happens when the user who triggered the workflow no longer exists in Azure DevOps? System should assign to a default fallback user or team lead configured in settings.
- How does the system handle Features that are already in 'Blocked' state when Issues are created? System should update the position to top of column and update assignment, but preserve the existing blocked state.
- What happens if the GitHub branch cannot be linked due to permission issues? System should log the error, notify the user, but continue with workflow execution for specification generation.
- How does the system determine which Azure DevOps Feature work item to link when multiple Features might match? System should use explicit Feature ID mapping from workflow context or fail with clear error message requesting clarification.
- What happens when spec.md file exists but is empty or corrupted? System should treat it as if spec.md does not exist and include Feature Description with Issue descriptions.
- How does the system handle Issue descriptions that contain special characters or formatting that might break input parsing? System should properly escape or sanitize Issue descriptions before passing to workflow.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST create a 'GitHub Branch' type link in the Azure DevOps Feature work item's Development tab immediately after creating a new feature branch
- **FR-002**: System MUST automatically move the parent Feature work item to 'Blocked' state when at least one Issue work item is created underneath it
- **FR-003**: System MUST position the blocked Feature work item at the top of the Blocked column in the Azure DevOps board view
- **FR-004**: System MUST assign the blocked Feature work item to the user who triggered the Specify workflow
- **FR-005**: System MUST determine whether a spec.md file exists for the current feature before processing workflow input
- **FR-006**: System MUST distinguish between closed and unclosed Issue work items when determining workflow input
- **FR-007**: System MUST pass both Feature Description and all unclosed Issue descriptions to the workflow when spec.md does not exist and unclosed Issues exist
- **FR-008**: System MUST pass only unclosed Issue descriptions to the workflow when spec.md exists and unclosed Issues exist
- **FR-009**: System MUST pass only Feature Description to the workflow when no Issues exist or all Issues are closed
- **FR-010**: System MUST maintain the association between GitHub branches and Azure DevOps Feature work items throughout the feature lifecycle
- **FR-011**: System MUST retrieve user identity from workflow context to assign Features correctly in Azure DevOps
- **FR-012**: System MUST authenticate with Azure DevOps API using secure credentials to perform work item operations
- **FR-013**: System MUST validate that the Feature work item exists in Azure DevOps before attempting to create links or modify its state
- **FR-014**: System MUST log all Azure DevOps integration operations for debugging and audit purposes

### Key Entities

- **Feature Work Item**: Azure DevOps work item representing a feature, contains Description, State (e.g., New, Blocked, Active), Assignment, and Development tab with links to related development artifacts
- **Issue Work Item**: Azure DevOps work item representing a clarification question or issue, child of Feature work item, has State (Open/Closed) and Description
- **GitHub Branch Link**: Development link in Azure DevOps that connects a Feature work item to a GitHub branch, type 'GitHub Branch'
- **Specify Workflow Context**: Contains information about the workflow execution including triggering user, Feature ID, branch name, and file system paths
- **Feature Description**: Text describing the feature requirements, stored in Azure DevOps Feature work item
- **spec.md File**: Markdown specification file stored in the GitHub repository feature branch at path specs/[feature-number]-[feature-name]/spec.md

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of new feature branches created by Specify workflow are automatically linked to their corresponding Azure DevOps Feature work items within 10 seconds of branch creation
- **SC-002**: Features with newly created Issues are moved to 'Blocked' state and assigned to the workflow initiator within 5 seconds of Issue creation
- **SC-003**: Specify workflow correctly determines input data (Feature Description vs Issue descriptions) based on spec.md existence and Issue state in 100% of executions
- **SC-004**: Users can view the GitHub branch link in Azure DevOps Development tab without manual intervention, reducing manual linking effort by 100%
- **SC-005**: Team leads can identify blocked features requiring attention by seeing them at the top of the Blocked column, improving visibility and reducing average time to address Issues by 50%
- **SC-006**: Workflow input handling correctly adapts to specification lifecycle (initial creation vs refinement), reducing incorrect specification updates by 90%

## Assumptions

- Azure DevOps API access is configured with appropriate permissions to create links, modify work item states, and update assignments
- The Specify workflow has access to the GitHub repository file system to check for spec.md existence
- User identity can be reliably retrieved from workflow context and mapped to Azure DevOps user accounts
- The Azure DevOps board is configured with a 'Blocked' column/state
- Issue work items are created as children of Feature work items in Azure DevOps hierarchy
- The GitHub branch naming convention follows the pattern used by the Specify workflow (e.g., 005-ado-specify-integration)
- Network connectivity between GitHub Actions and Azure DevOps services is reliable with reasonable latency
- The Feature ID or work item ID is available in the workflow context to identify the correct Azure DevOps Feature work item

## Dependencies

- Azure DevOps REST API availability and authentication
- Existing Specify workflow infrastructure in GitHub Actions
- Azure DevOps organization and project configuration with appropriate work item types (Feature, Issue)
- GitHub repository access permissions for the workflow to read/write branch information
- User account synchronization between GitHub and Azure DevOps for assignment mapping

## Out of Scope

- Synchronizing other GitHub artifacts (commits, pull requests, CI/CD runs) to Azure DevOps Development tab
- Automatically unblocking Features when all Issues are closed (manual or separate automation)
- Creating or modifying Azure DevOps work items beyond state changes and assignments
- Handling Features across multiple GitHub repositories
- Configuring or modifying Azure DevOps board layout, columns, or workflows
- Providing UI for users to manually trigger or configure the integration
- Rollback or cleanup of Azure DevOps changes if workflow fails after partial completion
