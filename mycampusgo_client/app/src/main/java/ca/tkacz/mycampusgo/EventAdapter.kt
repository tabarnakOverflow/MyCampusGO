package ca.tkacz.mycampusgo

import android.os.Build
import android.util.Log
import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.annotation.RequiresApi
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import ca.tkacz.mycampusgo.data.EventSummary
import ca.tkacz.mycampusgo.databinding.ItemEventBinding
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.time.format.FormatStyle

class EventAdapter(
    private val onClick: (EventSummary) -> Unit
) : ListAdapter<EventSummary, EventAdapter.VH>(Diff) {

    object Diff : DiffUtil.ItemCallback<EventSummary>() {
        override fun areItemsTheSame(oldItem: EventSummary, newItem: EventSummary) =
            oldItem.slug == newItem.slug

        override fun areContentsTheSame(oldItem: EventSummary, newItem: EventSummary) =
            oldItem == newItem
    }
// Make sure to change this if we can't require API 26
    @RequiresApi(Build.VERSION_CODES.O)
    fun convertTime(apiTime: String?): String {
        val instant = OffsetDateTime.parse(apiTime).toInstant()
        val timeZone = ZoneId.systemDefault()
        val zonedDateTime = instant.atZone(timeZone)
        val formatter = DateTimeFormatter.ofLocalizedDateTime(FormatStyle.MEDIUM, FormatStyle.SHORT);
        return zonedDateTime.format(formatter)
    }

    inner class VH(private val binding: ItemEventBinding) : RecyclerView.ViewHolder(binding.root) {
        @RequiresApi(Build.VERSION_CODES.O)
        fun bind(e: EventSummary) {
            binding.eventTitle.text = e.title
            binding.eventTime.text = convertTime(e.start ?: "")
            binding.eventLocation.text = e.location ?: ""
            binding.eventExcerpt.text = e.teaser ?: ""

            binding.root.setOnClickListener { onClick(e) }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val binding = ItemEventBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return VH(binding)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        holder.bind(getItem(position))
    }
}
