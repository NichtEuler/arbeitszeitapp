from arbeitszeit.use_cases import SendExtMessageRequest


class SendEmailController:
    def __call__(
        self, sender_email: str, receiver_email: str, title: str, content_html: str
    ) -> SendExtMessageRequest:
        return SendExtMessageRequest(
            sender_adress=sender_email,
            receiver_adress=receiver_email,
            title=title,
            content_html=content_html,
        )
