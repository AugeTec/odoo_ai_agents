/** @odoo-module **/

import {patch} from "@web/core/utils/patch";
import {ThreadService} from "@mail/core/common/thread_service";

/** @type {import("@mail/core/common/thread_service").ThreadService} */
const myThreadServicePatch = {
    async getMessagePostParams({
                                   attachments,
                                   body,
                                   cannedResponseIds,
                                   isNote,
                                   mentionedChannels,
                                   mentionedPartners,
                                   thread,
                               }) {
        let messagePostParams = await super.getMessagePostParams(...arguments);

        // resolve get params from url
        let url = window.location.href.split('#')[1];
        let urlParams = new URLSearchParams(url);

        // add frontend_context to messagePostParams
        let frontend_context = {}
        for (let key of urlParams.keys()) {
            frontend_context[key] = urlParams.get(key)
        }

        messagePostParams.context.frontend = frontend_context;
        console.log('messagePostParams', messagePostParams)
        return messagePostParams;
    }
};

patch(ThreadService.prototype, myThreadServicePatch);

