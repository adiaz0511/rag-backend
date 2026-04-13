# Backend Request Signing

This backend can require signed app requests for:

- `POST /ask`
- `POST /lesson`
- `POST /quiz`

## Required headers

- `X-App-Id`
- `X-App-Version`
- `X-Timestamp`
- `X-Nonce`
- `X-Signature`

## Signature algorithm

Use `HMAC-SHA256` with the shared secret from `APP_SHARED_SECRET`.

The message to sign is the UTF-8 byte sequence formed by joining these values with a newline:

1. HTTP method in uppercase
2. request path
3. timestamp
4. nonce
5. raw request body

Equivalent pseudocode:

```text
message = METHOD + "\n" + PATH + "\n" + TIMESTAMP + "\n" + NONCE + "\n" + RAW_BODY
signature = hex(HMAC_SHA256(APP_SHARED_SECRET, message))
```

## Example

For a request to `POST /ask` with body:

```json
{"query":"What symptoms mean I should call the transplant team?"}
```

Your iOS app should:

1. Serialize the JSON body exactly once.
2. Generate a Unix timestamp in seconds.
3. Generate a cryptographically random nonce.
4. Compute the signature over the exact bytes that will be sent.
5. Send the signed headers with the request.

## Verification behavior

The server rejects requests when:

- a required header is missing
- `X-App-Id` does not match `APP_ID`
- timestamp is older/newer than the allowed window
- nonce was already used recently
- signature does not match

## Deployment notes

- Never commit `APP_SHARED_SECRET` to git.
- Inject the same value into the deployed server and the app build process.
- In production, set `APP_ENV=production`.
- In production, the server fails closed if `APP_SHARED_SECRET` or `APP_ID` is missing.
- Keep `APP_DEBUG_LOGS=false` in production so prompts and model responses are not printed.
