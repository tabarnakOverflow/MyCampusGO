package ca.tkacz.mycampusgo

import android.os.Bundle
import android.util.Log
import android.view.View
import androidx.core.os.bundleOf
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import ca.tkacz.mycampusgo.R
import ca.tkacz.mycampusgo.data.ApiClient
import ca.tkacz.mycampusgo.databinding.FragmentEventsBinding
import kotlinx.coroutines.launch

class EventsFragment : Fragment(R.layout.fragment_events) {

    private var _binding: FragmentEventsBinding? = null
    private val binding get() = _binding!!

    private lateinit var adapter: EventAdapter

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentEventsBinding.bind(view)

        adapter = EventAdapter { event ->
            // Optional: navigate to detail by slug (set up nav graph first)
            findNavController().navigate(
                R.id.action_eventsFragment_to_eventDetailFragment,
                bundleOf("slug" to event.slug)
            )
        }

        binding.eventsRecycler.adapter = adapter

        binding.eventsRetry.setOnClickListener { loadEvents() }

        loadEvents()
    }

    private fun loadEvents() {
        showLoading()

        viewLifecycleOwner.lifecycleScope.launch {
            try {
                val events = ApiClient.api.getEvents(daysBack = 7)

                Log.d("EventsFragment", events.joinToString())

                if (events.isEmpty()) {
                    showMessage("No events found.")
                } else {
                    adapter.submitList(events)
                    showList()
                }
            } catch (e: Exception) {
                showMessage("Couldn’t load events.\n${e.message ?: ""}".trim(), showRetry = true)
            }
        }
    }

    private fun showLoading() {
        binding.eventsProgress.visibility = View.VISIBLE
        binding.eventsRecycler.visibility = View.GONE
        binding.eventsMessage.visibility = View.GONE
        binding.eventsRetry.visibility = View.GONE
    }

    private fun showList() {
        binding.eventsProgress.visibility = View.GONE
        binding.eventsRecycler.visibility = View.VISIBLE
        binding.eventsMessage.visibility = View.GONE
        binding.eventsRetry.visibility = View.GONE
    }

    private fun showMessage(msg: String, showRetry: Boolean = false) {
        binding.eventsProgress.visibility = View.GONE
        binding.eventsRecycler.visibility = View.GONE
        binding.eventsMessage.visibility = View.VISIBLE
        binding.eventsRetry.visibility = if (showRetry) View.VISIBLE else View.GONE
        binding.eventsMessage.text = msg
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
