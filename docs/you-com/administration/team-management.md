> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Team Management

## Overview

Organizations on the You.com Platform support multiple members with role-based access. Roles control who can create API keys, view usage, manage billing, and administer the organization itself.

Team management is available to organization accounts (Enterprise and API organization plans). Individual accounts do not have members or roles. Manage your team from **Settings → Members** on the [Platform](https://you.com/platform).

## Roles

Every member of an organization has exactly one role.

| Role          | Definition                                                                                                                         |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **Owner**     | Full control over the organization, members, and billing. The only role that can delete the organization or assign the Owner role. |
| **Admin**     | Manages members, settings, and API keys. Full access to everything except deleting the organization.                               |
| **Developer** | Creates and manages their own API keys. The default role for new invites.                                                          |
| **Billing**   | Read-only access to invoices and billing. For finance teammates who need payment information but should not see API keys.          |

Roles are fixed. There are no custom roles, and the permissions attached to each role cannot be edited.

## Permissions by Role

| Permission                          | Owner | Admin |    Developer    |     Billing     |
| ----------------------------------- | :---: | :---: | :-------------: | :-------------: |
| Create API keys                     |  Yes  |  Yes  |       Yes       |        No       |
| View own API keys                   |  Yes  |  Yes  |       Yes       |        No       |
| View all organization API keys      |  Yes  |  Yes  |        No       |        No       |
| Delete own API keys                 |  Yes  |  Yes  |       Yes       |        No       |
| View usage analytics                |  Yes  |  Yes  |        No       |        No       |
| View billing, invoices, and credits |  Yes  |  Yes  |        No       |       Yes       |
| Manage payment methods and credits  |  Yes  |  Yes  |        No       |        No       |
| View the member list                |  Yes  |  Yes  | Yes (read-only) | Yes (read-only) |
| Invite and remove members           |  Yes  |  Yes  |        No       |        No       |
| Change member roles                 |  Yes  |  Yes  |        No       |        No       |
| Assign the Owner role               |  Yes  |   No  |        No       |        No       |
| Edit the organization name          |  Yes  |  Yes  |        No       |        No       |
| Manage organization settings        |  Yes  |  Yes  |        No       |        No       |
| Delete the organization             |  Yes  |   No  |        No       |        No       |

Members can delete only the [API keys](/docs/administration/api-keys) they created. To revoke another member's keys, remove that member from the organization—their keys are deleted as part of removal.

### Role Notes

**Owner.** An organization can have multiple Owners, and must always have at least one. Owner is assigned by promotion only: an existing Owner changes a current member's role to Owner from the Members page. You cannot invite someone directly as an Owner.

**Admin.** Admins can do everything an Owner can except delete the organization and assign the Owner role. Admins can invite and manage members with the Admin, Developer, or Billing role.

**Developer.** Developers see only the keys they created—other members' keys are not visible to them. They have no access to billing, analytics, member management, or organization settings, though they can view the member list in read-only mode.

**Billing.** Billing members see invoices, payment methods, and credit balance, but cannot change them. Adding or removing a payment method, purchasing credits, and configuring Auto Top-Up all require Admin or Owner. API keys and usage analytics are hidden from their navigation entirely.

## Inviting Members

Only Owners and Admins can invite members.

1. Go to **Settings → Members** on the [Platform](https://you.com/platform)
2. Click **Invite**
3. Enter one or more email addresses
4. Select a role for the invitees—the default is **Developer**
5. Send the invite

The role selector at invite time offers Admin, Developer, and Billing. Owner is not available—see [Role Notes](#role-notes).

Pending invites appear in the members table with an **Invited** status. You can resend or revoke a pending invite at any time.

**If the invitee already has a You.com account:** they are added to your organization when they accept, provided they do not already belong to another organization. An account can belong to only one organization—if the invited email is already a member of a different organization, the invite cannot be completed. Contact [support](https://you.com/support) if you need to move an account between organizations.

## Changing Roles

Owners and Admins can change member roles inline from the Members page. Two rules apply:

* You can assign only roles at or below your own level. Admins can assign Admin, Developer, or Billing—only an Owner can assign Owner.
* The last Owner cannot be demoted. Promote another member to Owner first.

Role changes that remove access take effect on the member's next request—no sign-out required. Role changes that grant new access can take a few minutes to propagate. The member can sign out and back in to pick up new permissions immediately.

## Removing Members

Owners and Admins can remove members from the Members page.

Removing a member permanently deletes all API keys they created. Requests using those keys fail immediately, and keys are not transferable to another member. Before removing a member whose keys are in production, create replacement keys under another account and update your applications first.

The last Owner of an organization cannot be removed.

## Organization Settings

The **Settings → Organization** page shows:

* **Organization name**—editable by Owners and Admins
* **Organization ID**—read-only. Use the copy control when contacting support.
* **Delete organization**—restricted to Owners. To delete your organization, contact [support](https://you.com/support).

## Constraints

* An organization must always have at least one Owner. The last Owner cannot be demoted or removed.
* Multiple Owners are allowed and recommended, so the organization is not dependent on a single account.
* Owner is assigned by promotion only, never at invite. Only an Owner can assign the Owner role.
* Members can assign only roles at or below their own level.
* An account can belong to only one organization at a time.
* Removing a member permanently deletes their API keys. There is no key transfer.
* Roles are predefined. Custom roles and per-member permission edits are not supported.
* Member and organization changes—invites, role changes, removals, and settings updates—are recorded in an audit log.

## Questions & Support

For questions about team management or to request changes that require support (organization deletion, moving an account between organizations), contact [support](https://you.com/support) or email [api@you.com](mailto:api@you.com).