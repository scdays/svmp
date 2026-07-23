# Git Diff Analysis: feature/fix-ledger-log-records

> Analysis comparing `bb773bbe8eaf1e888a933dc81697f037ef2f1d5b` (base) to `fe19386` (head)

---

## 1. .eslintrc.js

**File**: `.eslintrc.js`  
**Change type**: PURE-ADDITIVE (cosmetic only)

**What changed**:
- Changed double quotes to single quotes on line 57: `indent: 'off'` (was `indent: "off"`)

**Existing-code impact**: None - this is purely a quote-style cosmetic change with no functional impact.

**Risk to other functionality**: **LOW** - This is an ESLint config style change only, no runtime impact.

---

## 2. src/App.vue

**File**: `src/App.vue`  
**Change type**: SUBSTANTIVE-EDIT (core app behavior change)

**What changed**:
- **Replaced** `<router-view :key="$route.fullPath" />` with `<router-view :key="routeViewKey" />`
- **Added** import: `import { buildStableRouteKey } from '@/views/VulnManagePlat/utils/stableRouteKey'`
- **Added** computed property `routeViewKey` that returns `buildStableRouteKey(this.$route)`
- **Added** comment explaining the change: "禁止用 fullPath 做 key：?_sub / ?_from 属于全页子页内部状态，用 fullPath 会导致进子页/返回时整棵路由树销毁重建，列表像冷启动一样慢。"

**Existing-code impact**:
- **Removed** `$route.fullPath` as the router-view key
- **Changed** the root router-view re-render behavior - no longer destroys/re-creates the entire component tree when query params like `_sub`, `_from`, or `refresh` change

**Risk to other functionality**: **HIGH** - This affects the entire application's routing behavior. The change is designed to improve performance by preventing unnecessary re-renders, but any component relying on being re-mounted when those query params change could be affected.

---

## 3. src/api/Assembly/AssemblyUrl.js

**File**: `src/api/Assembly/AssemblyUrl.js`  
**Change type**: PURE-ADDITIVE (whitespace only)

**What changed**:
- Only change appears to be adding a newline at the end of the file (no functional changes)
- The `accList` export is unchanged

**Existing-code impact**: None

**Risk to other functionality**: **LOW** - No functional changes, just a trailing newline.

---

## 4. src/api/Assembly/NewLeakVulnInfo.js

**File**: `src/api/Assembly/NewLeakVulnInfo.js`  
**Change type**: ADDITIVE+MINOR-EDIT

**What changed**:
- **Added** 8 new API endpoints for "主任务自动化处置（Wave J）":
  - `previewVulScanTaskAutoDispose`
  - `startVulScanTaskAutoDispose`
  - `getVulScanTaskAutoDispose`
  - `pauseVulScanTaskAutoDispose`
  - `resumeVulScanTaskAutoDispose`
  - `notifyVulScanTaskAutoDispose`
  - `getActiveVulScanTaskAutoDispose`

**Existing-code impact**: None - only additive, no existing endpoints changed or removed.

**Risk to other functionality**: **LOW** - New API endpoints only, no existing functionality modified.

---

## 5. src/components/MultiTab/MultiTab.vue

**File**: `src/components/MultiTab/MultiTab.vue`  
**Change type**: SUBSTANTIVE-EDIT (shared core component)

**What changed**:
- **Added** import: `import { buildStableRouteKey, pushByStableRouteKey } from '@/views/VulnManagePlat/utils/stableRouteKey'`
- **Changed** `created()`: Now uses `buildStableRouteKey()` instead of `$route.fullPath`
- **Changed** `$route` watcher: Now ignores `_sub`, `_from`, and `refresh` query params
- **Changed** `activeKey` watcher: Now uses `pushByStableRouteKey()` and avoids pushing if already on the same route

**Existing-code impact**:
- **Modified** how tabs are tracked and navigated: Tabs are now based on stable route keys that ignore internal query parameters
- **Changed** `pages` array items: Now stores routes with `fullPath` replaced by the stable key
- **Changed** `fullPathList` array: Now stores stable keys instead of raw fullPaths

**Risk to other functionality**: **HIGH** - MultiTab is a shared component used across the entire application. The change affects:
- How tabs are created (no more duplicate tabs for the same page with different `_sub` query params)
- How tab switching navigates
- Which routes are considered "the same" for tab management

This could break any functionality that relies on different query params creating separate tabs.

---

## 6. src/config/router.config.js

**File**: `src/config/router.config.js`  
**Change type**: SUBSTANTIVE-EDIT (route configuration)

**What changed**:
- **Updated** 8 route component paths to point to `/subpages/Entry` instead of the original component:
  - `ProVulnWarnTask` → `ProVulnWarnTask/subpages/Entry`
  - `ProVulnUploadTask` → `ProVulnUploadTask/subpages/Entry`
  - `ProVulnSyncTask` → `ProVulnSyncTask/subpages/Entry`
  - `PassDicSyncTask` → `PassDicSyncTask/subpages/Entry`
  - `PassDicUploadTask` → `PassDicUploadTask/subpages/Entry`
  - `GangedTask` → `GangedTask/subpages/Entry`
  - `SysVulnOrder` → `SysVulnOrder/subpages/Entry`
  - `ProduntVulnOrder` → `ProduntVulnOrder/subpages/Entry`

**Existing-code impact**:
- **Replaced** the component entry points for these 8 routes
- The original components are still present but no longer directly routed to

**Risk to other functionality**: **MEDIUM** - Route structure has changed. If other code references these components directly (not via routing), it should still work. But any code that relies on the old component structure could be affected. The new `subpages/Entry` pattern suggests a move to a sub-page navigation architecture.

---

## 7. src/views/VulnManagePlat/components/ReturnHistory/ReturnHistory.vue

**File**: `src/views/VulnManagePlat/components/ReturnHistory/ReturnHistory.vue`  
**Change type**: ADDITIVE+MINOR-EDIT

**What changed**:
- **Added** mixin: `import drawerPageMode from '@/views/VulnManagePlat/mixins/drawerPageMode'`
- **Added** `mixins: [drawerPageMode]`
- **Changed** template root: Replaced `<a-drawer>` with `<component :is="wrapperTag" v-bind="drawerBind">`
- **Added** computed `drawerBind` that conditionally renders either drawer props or a div class
- **Modified** `visible` prop: Changed from `required: true` to `default: true`
- **Modified** `close()` method: Now checks `pageMode` and emits `page-back` instead of `close`
- **Modified** `seeDetail()` method: Now checks `pageMode` and emits `page-navigate` instead of opening drawer
- **Added** conditional on cancel button: `v-if="!pageMode"`

**Existing-code impact**:
- **Changed** the component's root element from always being a-drawer to being conditionally a drawer or div
- **Modified** event emission behavior based on pageMode

**Risk to other functionality**: **LOW-MEDIUM** - The changes are backward-compatible when `pageMode` is not provided (defaults to false). The component still behaves like a drawer by default.

---

## 8. src/views/VulnManagePlat/components/ReturnHistory/ReturnHistoryDrawer.vue

**File**: `src/views/VulnManagePlat/components/ReturnHistory/ReturnHistoryDrawer.vue`  
**Change type**: ADDITIVE+MINOR-EDIT

**What changed**:
- **Added** mixin: `import drawerPageMode from '@/views/VulnManagePlat/mixins/drawerPageMode'`
- **Added** `mixins: [drawerPageMode]`
- **Changed** template root: Replaced `<a-drawer>` with `<component :is="wrapperTag" v-bind="drawerBind">`
- **Added** computed `drawerBind` similar to ReturnHistory.vue
- **Modified** `visible` prop: Changed from `required: true` to `default: true`
- **Modified** `close()` method: Now checks `pageMode` and emits `page-back`
- **Added** conditional on cancel button: `v-if="!pageMode"`

**Existing-code impact**: Same pattern as ReturnHistory.vue - conditionally supports pageMode.

**Risk to other functionality**: **LOW-MEDIUM** - Backward-compatible by default.

---

## 9. src/views/VulnManagePlat/components/TaskDetails/ProMethodDrawer.vue

**File**: `src/views/VulnManagePlat/components/TaskDetails/ProMethodDrawer.vue`  
**Change type**: SUBSTANTIVE-EDIT

**What changed**:
- **Added** imports for report type constants: `CONNECTIVITY_REPORT_TYPE`, `resolveScanReportType`
- **Added** `BASE_CHECK_DATA` constant array (moved from data())
- **Added** new prop `source` (for 企业本地/部侧 distinction)
- **Added** computed `resolvedSource` that prioritizes prop > model.source
- **Moved** dynamic checkData construction from `created()` to new `buildCheckData()` method
- **Added** `applyInitialReportType()` method with smart defaults for verify-fix phase
- **Added** handling for `tskPhase === '4'` (verify-fix phase)
- **Changed** `created()`: Now uses `buildCheckData()` and `applyInitialReportType()` instead of inline logic

**Existing-code impact**:
- **Removed** hardcoded `ctxReportType` logic (was `this.model.ctxCode === 2 ? 3 : 10`)
- **Removed** static `checkData` from data() (now built dynamically)
- **Changed** how `reportType` is initialized: Now respects existing `model.reportType` first, then applies smart defaults
- **Added** connectivity check now uses constant `CONNECTIVITY_REPORT_TYPE`

**Risk to other functionality**: **MEDIUM** - Significant logic changes to how checkData and reportType are determined. The new logic appears more flexible but could introduce regressions if the `resolveScanReportType` function doesn't behave the same as the old hardcoded logic in all cases.

---

## 10. src/views/VulnManagePlat/components/TaskDetails/SearchTask/SearchTask.vue

**File**: `src/views/VulnManagePlat/components/TaskDetails/SearchTask/SearchTask.vue`  
**Change type**: ADDITIVE+MINOR-EDIT

**What changed**:
- **Added** mixin: `drawerPageMode`
- **Added** new prop `embedded` (boolean, default false)
- **Changed** template root: Replaced `<a-drawer>` with `<component :is="wrapperTag" v-bind="drawerBind">`
- **Added** computed `wrapperTag` that returns 'div' if `pageMode || embedded`, otherwise 'a-drawer'
- **Added** computed `drawerBind` similar to other components
- **Modified** `visible` prop: Changed from `required: true` to `default: true`
- **Modified** `close()` method: Now checks `pageMode`
- **Added** conditional on cancel button: `v-if="!pageMode && !embedded"`
- **Removed** the "处置" button entirely (was conditionally rendered)

**Existing-code impact**:
- **Removed** the "处置" (disposition) button from the UI
- **Added** embedded mode support

**Risk to other functionality**: **MEDIUM** - Removal of the "处置" button could be a breaking change if other code expects it to be there. The pageMode/embedded changes are backward-compatible.

---

## 11. src/views/VulnManagePlat/components/TaskDetails/TaskDetailDrawer.vue

**File**: `src/views/VulnManagePlat/components/TaskDetails/TaskDetailDrawer.vue`  
**Change type**: PURE-ADDITIVE (minor)

**What changed**:
- **Removed** `ellipsis: true` from 10 column definitions in the `columns` array:
  - assetName
  - isAccess
  - vulInfoStat
  - srcMethod
  - lvRsn
  - vulName
  - orgVulId
  - vulPriorVal
  - vulPriorLvl
  - vulPriorMid

**Existing-code impact**: Removed ellipsis truncation from these table columns.

**Risk to other functionality**: **LOW** - Only affects table column display; text will no longer be truncated with ellipsis.

---

## 12. src/views/VulnManagePlat/components/TaskDetails/TaskDrawer.vue

**File**: `src/views/VulnManagePlat/components/TaskDetails/TaskDrawer.vue`  
**Change type**: SUBSTANTIVE-EDIT (833 lines changed - MAIN WORKBENCH COMPONENT)

**Note**: This is the largest change and appears to be the core of the "工作台" (workbench) feature.

**What changed (key highlights)**:
- **Changed** root element from `<a-drawer>` to `<component :is="wrapperTag" v-bind="drawerBind">` (supports pageMode/embedded)
- **Added** mixin: `drawerPageMode`
- **Added** new props: `embedded`, `source`, `activeTabKey`
- **Completely reworked** the template structure:
  - Removed the main table view
  - Added a tabbed interface with multiple tabs
  - Added integrated TaskInfoDrawer, SearchTask, and other components directly
  - Added "日志台账" (log ledger) tab
  - Added a bottom action bar with "处置" button
- **Added** extensive new logic for sub-page navigation, log ledger viewing, auto-dispose, etc.
- **Added** many new data properties, computed properties, and methods
- **Removed** the original table-based layout

**Existing-code impact**:
- **Rewrote** the entire component - this is essentially a complete replacement
- **Changed** from a drawer showing a task list to an embedded workbench with multiple views
- **Removed** the original table expansion behavior
- **Removed** the standalone refresh button (moved to tab-specific refreshes)

**Risk to other functionality**: **HIGH** - This component appears to be the main task details view. If any parent components or routes were using the old TaskDrawer with its previous API, they will likely break. The component's props have changed, its template structure has changed, and its behavior is completely different.

---

## 13. src/views/VulnManagePlat/components/TaskDetails/TaskInfoDrawer.vue

**File**: `src/views/VulnManagePlat/components/TaskDetails/TaskInfoDrawer.vue`  
**Change type**: ADDITIVE+MINOR-EDIT

**What changed**:
- **Added** mixin: `drawerPageMode`
- **Added** new props: `embedded`, `source`
- **Changed** template root: Replaced `<a-drawer>` with `<component :is="wrapperTag" v-bind="drawerBind">`
- **Added** computed `wrapperTag` and `drawerBind`
- **Modified** `visible` prop: Changed from `required: true` to `default: true`
- **Modified** `close()` method: Now checks `pageMode`
- **Added** conditional on cancel button: `v-if="!pageMode && !embedded"`
- **Added** `:source="source"` prop binding to ProMethodDrawer
- **Removed** `console.log('guanlema')`

**Existing-code impact**: Added pageMode/embedded support, passed source to ProMethodDrawer.

**Risk to other functionality**: **LOW-MEDIUM** - Backward-compatible by default.

---

## 14. src/views/VulnManagePlat/components/TaskSend/AddTaskDrawer.vue

**File**: `src/views/VulnManagePlat/components/TaskSend/AddTaskDrawer.vue`  
**Change type**: SUBSTANTIVE-EDIT

**What changed**:
- **Added** `@verifyFixPlanChange="onVerifyFixPlanChange"` event listener to BaseInfo
- **Added** condition to SafeSourceDriver template: `&& !isVerifyFixConfirm`
- **Added** new computed properties: `isVerifyFixConfirm`, `verifyFixDevicesOk`, `verifyFixConfirmDisabled`
- **Added** new data property: `verifyFixPlan`
- **Changed** button text from "下发" to dynamic: `{{ isVerifyFixConfirm ? '确认下发' : '下发' }}`
- **Changed** button disabled binding to use `verifyFixConfirmDisabled`
- **Added** new methods: `onVerifyFixPlanChange`, `resolveConfirmToken`
- **Rewrote** `saveorSubmit()` method with extensive new logic:
  - Added try-catch around BaseInfo submit
  - Added verify-fix phase (phase 4) validation
  - Added confirmToken handling
  - Added verifyFixDevicesOk validation
  - Added auto-population of engHashes from verifyFixPlan
  - Added `source` to params
  - Added `confirmToken` to params when present
  - Improved error message: `(err && err.message) || '保存失败'`
- **Removed** commented-out async getData() method

**Existing-code impact**:
- **Modified** SafeSourceDriver visibility: Now hidden when `isVerifyFixConfirm` is true
- **Changed** how "下发" button behaves: Now has different text and validation in verify-fix mode
- **Changed** form submission logic: Now handles the verify-fix confirmation flow

**Risk to other functionality**: **MEDIUM-HIGH** - Significant changes to the task submission flow, especially for the verify-fix phase (phase 4). Could break existing task submission if the new validation logic is too strict or if confirmToken isn't handled correctly.

---

## 15. src/views/VulnManagePlat/components/TaskSend/BaseInfo.vue

**File**: `src/views/VulnManagePlat/components/TaskSend/BaseInfo.vue`  
**Change type**: SUBSTANTIVE-EDIT

**What changed**:
- **Changed** text "离线导入" → "离线任务" in the tskModel tag
- **Added** `<VerifyFixPlanPreview>` component at the bottom of the template
- **Added** import: `import VerifyFixPlanPreview from './VerifyFixPlanPreview.vue'`
- **Added** `VerifyFixPlanPreview` to components
- **Added** API call to get `VulReportTypeEnum` in created()
- **Added** new data properties: `verifyFixPlan`, `reportTypeData`
- **Rewrote** `getData()` method extensively:
  - Now passes `procMethod` and `source` to the API
  - Added error handling for non-1 response codes
  - Added handling for `verifyFixPlan` in response
  - Added handling for `confirmToken`
  - Added warning for phase 4 without confirmToken
  - Added event emission for `verifyFixPlanChange`
  - Improved error messages
- **Added** `$emit('changeTskPhase', this.watchTskPhase)` in tskPhase watcher to sync with parent

**Existing-code impact**:
- **Changed** API call parameters: Now includes `procMethod` and `source`
- **Changed** component's event emissions: Now emits `verifyFixPlanChange`
- **Added** child component VerifyFixPlanPreview (assumed to be a new file)

**Risk to other functionality**: **MEDIUM-HIGH** - The API call contract has changed (now passes more parameters). The parent component AddTaskDrawer relies on the new events and confirmToken flow. If the backend doesn't support the new parameters or if VerifyFixPlanPreview component is missing, this could break.

---

## Overall Summary & Risk Assessment

### Key Themes

This branch implements two major features:

1. **Sub-page Architecture**: A new navigation pattern that allows drawers to operate as full pages using query params (`_sub`, `_from`) instead of always being modal drawers. This affects:
   - `App.vue` (router-view key change)
   - `MultiTab.vue` (tab creation/navigation)
   - Multiple drawer components (via `drawerPageMode` mixin)

2. **Repair Verification (修复核验)**: A new workflow for phase 4 tasks, including:
   - Preview of repair plans
   - Confirm tokens
   - Device matching validation
   - New API endpoints

### Risk Breakdown

| Risk Level | Components | Reason |
|-----------|-----------|--------|
| **HIGH** | `App.vue`, `MultiTab.vue`, `TaskDrawer.vue` | Core app behavior changes affecting routing, tabs, and the main workbench |
| **MEDIUM-HIGH** | `AddTaskDrawer.vue`, `BaseInfo.vue`, `ProMethodDrawer.vue` | Significant workflow changes to task submission with new validations |
| **MEDIUM** | `router.config.js`, `SearchTask.vue` | Route structure changes, removed "处置" button |
| **LOW-MEDIUM** | `ReturnHistory.vue`, `ReturnHistoryDrawer.vue`, `TaskInfoDrawer.vue` | Added pageMode support (backward-compatible) |
| **LOW** | `.eslintrc.js`, `AssemblyUrl.js`, `NewLeakVulnInfo.js`, `TaskDetailDrawer.vue` | Cosmetic, additive, or minor display changes |

### Critical Dependencies to Check

1. **New utility files** (not in diff but referenced):
   - `src/views/VulnManagePlat/utils/stableRouteKey.js` ✓ exists
   - `src/views/VulnManagePlat/mixins/drawerPageMode.js` ✓ exists
   - `src/views/VulnManagePlat/components/TaskSend/VerifyFixPlanPreview.vue` (needs verification)
   - `src/views/VulnManagePlat/constants/reportTypeAssign.js` (needs verification)

2. **Backend API changes**: The frontend now expects:
   - `verifyFixPlan` and `confirmToken` in `getVulnScanTaskPreDispatch` response
   - New endpoints for auto-dispose (already added to API file)
   - `source` parameter support in relevant endpoints

3. **Route components**: The 8 routes pointing to `/subpages/Entry` require those new Entry components to exist.

### Recommendations

1. **High Risk**: Thoroughly test tab navigation and routing behavior, especially with routes that use `_sub` query params.
2. **High Risk**: Test the new TaskDrawer workbench extensively, as it's a complete rewrite.
3. **Medium-High**: Test the repair verification (修复核验) workflow end-to-end, including device matching and confirm tokens.
4. **Medium**: Verify all 8 new `/subpages/Entry` components exist and work correctly.
5. **General**: Check that no other parts of the app relied on the removed "处置" button in SearchTask.
