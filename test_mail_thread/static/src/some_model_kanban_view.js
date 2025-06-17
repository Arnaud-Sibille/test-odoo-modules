import { registry } from "@web/core/registry";

import { Chatter } from "@mail/chatter/web_portal/chatter";

import { KanbanController } from "@web/views/kanban/kanban_controller";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { kanbanView } from "@web/views/kanban/kanban_view";

class SomeModelKanbanRenderer extends KanbanRenderer {

}

class SomeModelKanbanController extends KanbanController {
    static template = "test_mail_thread.SomeModelKanbanController";
    static components = {
        ...KanbanController.components,
        Chatter,
    }
}

const someModelKanbanView = {
    ...kanbanView,
    Renderer: SomeModelKanbanRenderer,
    Controller: SomeModelKanbanController,
};

registry.category("views").add("some_model_kanban", someModelKanbanView);
