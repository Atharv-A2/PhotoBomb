import com.example.photobomb.app.data.datastore.AuthPreferences
import okhttp3.Interceptor
import okhttp3.Response
import kotlinx.coroutines.runBlocking

class AuthInterceptor(
    private val authPreferences:
    AuthPreferences
) : Interceptor {

    override fun intercept(
        chain: Interceptor.Chain
    ): Response {

        val request =
            chain.request()

        val path =
            request.url.encodedPath

        if (
            path.contains("/auth/login")
            || path.contains("/auth/register")
            || path.contains("/auth/refresh")
        ) {
            return chain.proceed(
                request
            )
        }

        val token =
            runBlocking {
                authPreferences
                    .getAccessToken()
            }

        if (
            token.isNullOrBlank()
        ) {
            return chain.proceed(
                request
            )
        }

        val authenticated =
            request.newBuilder()
                .addHeader(
                    "Authorization",
                    "Bearer $token"
                )
                .build()

        return chain.proceed(
            authenticated
        )
    }
}